"""Điều phối toàn bộ flow: brief → router → gap → clarify (Stop pre) →
   research → meeting → synthesizer (Stop 1) → execution (Stop 2)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import re

from core.brain.reader import BrainReader
from core.brain.gap_analyzer import GapAnalyzer
from core.clarifier.question_generator import QuestionGenerator
from core.clarifier.clarification_io import (
    write_clarification, read_answers,
)
from core.obsidian.vault import ObsidianVault
from core.orchestrator.router import Router
from core.utils.config import load_config


class FlowStage(str, Enum):
    PAUSE_CLARIFICATION = "PAUSE_CLARIFICATION"
    PAUSE_DECISION_REPORT = "PAUSE_DECISION_REPORT"
    PAUSE_EXECUTE = "PAUSE_EXECUTE"
    DONE = "DONE"
    ERROR = "ERROR"


@dataclass
class FlowResult:
    stage: FlowStage
    task_folder: Path
    message: str = ""
    error: Optional[str] = None


def _slugify(brief: str, max_len: int = 50) -> str:
    s = re.sub(r"[^\w\s-]", "", brief.lower())
    s = re.sub(r"\s+", "-", s.strip())[:max_len]
    return s.strip("-") or "task"


class FlowController:
    def __init__(self, vault_root: Path, llm):
        self.vault = ObsidianVault(vault_root)
        self.llm = llm
        self.config = load_config()

    def run(self, brief: str) -> FlowResult:
        """Stage 1: brief → router → gap → clarification (PAUSE)."""
        # 1. Create task folder
        task_folder = self.vault.create_task_folder(_slugify(brief))
        (task_folder / "00-brief.md").write_text(
            f"---\ntype: brief\n---\n# Brief\n\n{brief}\n", encoding="utf-8",
        )

        # 2. Read Brain
        brain = BrainReader(self.vault.root).load()

        # 3. Router classify
        rules_path = Path(__file__).parent / "classifier_rules.yaml"
        router = Router(self.llm, rules_path=rules_path)
        classification = router.classify(brief, brain)

        (task_folder / "01-routing.md").write_text(
            f"---\ntype: routing\n---\n# Phân loại task\n\n"
            f"- **Class:** {classification.class_.value}\n"
            f"- **Departments:** {', '.join(classification.departments)}\n"
            f"- **Reasoning:** {classification.reasoning}\n",
            encoding="utf-8",
        )

        # 4. Context dump
        (task_folder / "02-context.md").write_text(
            "---\ntype: context\n---\n# Brain context loaded\n\n"
            f"```yaml\n{brain.model_dump_json(indent=2)}\n```\n",
            encoding="utf-8",
        )

        # 5. Gap analysis
        analyzer = GapAnalyzer(self.llm)
        gaps = analyzer.analyze(brief, brain)

        if not gaps:
            return FlowResult(
                stage=FlowStage.PAUSE_DECISION_REPORT,
                task_folder=task_folder,
                message="Không có gap, sẵn sàng chạy meeting (Phase 4+5 sẽ wire).",
            )

        # 6. Generate questions
        qg = QuestionGenerator(self.llm)
        questions = qg.generate(gaps, brain.model_dump(), brief)

        if not questions:
            return FlowResult(
                stage=FlowStage.PAUSE_DECISION_REPORT,
                task_folder=task_folder,
                message="Gap có nhưng không CRITICAL/WARN, skip clarification.",
            )

        # 7. Write clarification + PAUSE
        clarification_path = task_folder / "03-clarification.md"
        write_clarification(clarification_path, questions)

        return FlowResult(
            stage=FlowStage.PAUSE_CLARIFICATION,
            task_folder=task_folder,
            message=f"Vui lòng trả lời {len(questions)} câu trong {clarification_path.name}",
        )

    def resume_after_clarification(self, task_folder: Path) -> FlowResult:
        """Stage 2: read answers → continue flow (Phase 4+ sẽ wire research+meeting)."""
        clarification_path = task_folder / "03-clarification.md"
        if not clarification_path.exists():
            return FlowResult(
                stage=FlowStage.ERROR, task_folder=task_folder,
                error="Không tìm thấy 03-clarification.md",
            )

        answers = read_answers(clarification_path)
        unanswered = [a for a in answers if a.choice is None and not a.free_text_answer]
        if unanswered:
            return FlowResult(
                stage=FlowStage.PAUSE_CLARIFICATION,
                task_folder=task_folder,
                message=f"Còn {len(unanswered)} câu chưa trả lời",
            )

        # Save normalized answers
        (task_folder / "03-clarification-answered.md").write_text(
            "---\ntype: answers\n---\n"
            + "\n".join(f"- Q: {a.question_text}\n  A: {a.choice or a.free_text_answer}"
                       for a in answers),
            encoding="utf-8",
        )

        # Phase 4-5 wires research + meeting here
        return FlowResult(
            stage=FlowStage.PAUSE_DECISION_REPORT,
            task_folder=task_folder,
            message="Đã ghi nhận trả lời. Phase 4+5 sẽ wire research + meeting.",
        )

    def run_meeting(self, task_folder: Path, departments: list[str]) -> FlowResult:
        """Stage 3: research → meeting → synthesizer → STOP 1."""
        from core.brain.reader import BrainReader
        from core.orchestrator.research_phase import ResearchPhase
        from core.orchestrator.perspectives_collector import PerspectivesCollector
        from core.meeting.meeting_graph import MeetingGraph
        from core.meeting.debate_state import new_meeting_state
        from core.translator.pipeline import TranslatorPipeline
        from core.obsidian.git_sync import GitSync

        brief = self._read_brief(task_folder)
        brain = BrainReader(self.vault.root).load()

        # 1. Research phase (RULE 5)
        research = ResearchPhase(self.llm)
        findings = research.run(
            brief=brief,
            brain_summary=brain.model_dump_json()[:3000],
            task_folder=task_folder,
        )

        # 2. Meeting graph
        departments_root = Path(__file__).parent.parent.parent / "departments"
        collector = PerspectivesCollector(departments_root, self.llm)

        graph = MeetingGraph(
            llm=self.llm,
            perspectives_collector=collector.collect,
            checkpointer=False,  # disable for now to avoid SQLite issues
        )

        state = new_meeting_state(
            brief=brief,
            departments=departments,
            brain_context=brain.model_dump(),
            max_rounds=self.config.meeting.max_debate_rounds,
            task_id=task_folder.name,
        )
        state["research_findings"] = findings

        final_state = graph.build().invoke(state)

        # 3. Write meeting outputs
        self._write_meeting_outputs(task_folder, final_state)

        # 4. Translator pipeline (RULE 4) on final_report
        glossary_path = self.vault.root / "00-Brain" / "glossary.md"
        translator = TranslatorPipeline(self.llm, vault_glossary_path=glossary_path)
        translated_report = translator.apply(final_state["final_report"])

        decision_path = task_folder / "07-decision-report.md"
        decision_path.write_text(
            f"---\ntype: decision_report\nstop: 1\n---\n{translated_report}",
            encoding="utf-8",
        )

        # 5. Auto-commit (best-effort)
        try:
            GitSync(self.vault.root).commit(
                f"feat(task): {task_folder.name} — decision report ready (Stop 1)"
            )
        except Exception:
            pass

        return FlowResult(
            stage=FlowStage.PAUSE_DECISION_REPORT,
            task_folder=task_folder,
            message=f"Decision report sẵn ở {decision_path.name}. CEO đọc + duyệt.",
        )

    def _read_brief(self, task_folder: Path) -> str:
        brief_md = (task_folder / "00-brief.md").read_text(encoding="utf-8")
        parts = brief_md.split("---", 2)
        return (parts[2] if len(parts) >= 3 else brief_md).strip()

    def _write_meeting_outputs(self, task_folder: Path, state):
        perspectives_md = "\n\n".join(
            f"## {dept}\n\n{p}" for dept, p in state["perspectives"].items()
        )
        (task_folder / "04-meeting-r1-perspectives.md").write_text(
            f"---\ntype: meeting_r1\n---\n# Round 1 — Perspectives\n\n{perspectives_md}",
            encoding="utf-8",
        )

        debate_md = "\n\n".join(state["pro_con_debate"]["history"])
        (task_folder / "05-meeting-r2-debate.md").write_text(
            f"---\ntype: meeting_r2\n---\n# Round 2 — Pro/Con Debate\n\n{debate_md}",
            encoding="utf-8",
        )

        perspective_md = "\n\n".join(state["perspective_debate"]["history"])
        (task_folder / "06-meeting-r3-perspectives.md").write_text(
            f"---\ntype: meeting_r3\n---\n# Round 3 — Perspective Debate\n\n{perspective_md}",
            encoding="utf-8",
        )

    def approve_decision(self, task_folder: Path, decision: str = "approve") -> FlowResult:
        """Stage 4: CEO duyệt decision report → execution plan."""
        # Stub for v1 — Phase 6 wires actual execution plan generation
        (task_folder / "08-execution-plan.md").write_text(
            "---\ntype: execution_plan\nstop: 2\n---\n# Execution Plan\n\n(TODO Phase 6: generate from decision report)",
            encoding="utf-8",
        )
        return FlowResult(
            stage=FlowStage.PAUSE_EXECUTE,
            task_folder=task_folder,
            message="Execution plan stub created. Run 'execute' to generate output docs.",
        )

    def execute(self, task_folder: Path) -> FlowResult:
        """Stage 5: render docs → 03-Outputs/."""
        # Stub for v1 — Phase 6 wires DocWriter + TemplateResolver
        outputs_dir = self.vault.root / "03-Outputs" / task_folder.name
        outputs_dir.mkdir(parents=True, exist_ok=True)
        (outputs_dir / "README.md").write_text(
            f"# Outputs for {task_folder.name}\n\n(TODO Phase 6: render .docx/.xlsx via DocWriter)",
            encoding="utf-8",
        )
        return FlowResult(
            stage=FlowStage.DONE,
            task_folder=task_folder,
            message=f"Done. Outputs at {outputs_dir.relative_to(self.vault.root)}",
        )
