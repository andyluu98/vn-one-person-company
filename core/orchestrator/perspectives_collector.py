"""Round 1 — moi phong phat bieu goc nhin (parallel).

P1.1 fix: load per-agent enriched system prompt tu <departments_root>/<dept>/agents/<default_speaker>.md
qua AgentLoader. Fallback sang generic PERSPECTIVE_PROMPT neu file missing.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from core.agents.department import DepartmentLoader
from core.agents.agent_loader import AgentLoader
from core.agents.base_agent import BaseAgent
from core.meeting.debate_state import MeetingState


PERSPECTIVE_PROMPT = """Ban la phong {dept_name} trong DN VN.

Doc brief + Brain context. Phat bieu GOC NHIN cua phong ban:
- Phong ban quan tam dieu gi trong brief nay?
- Co hoi / rui ro tu goc do phong ban?
- So lieu Brain lien quan (cite cu the)?
- De xuat ngan gon

Tieng Viet. Dinh nghia thuat ngu. Cite Brain moi nhan dinh.
KHONG dai qua 400 tu — day la round 1.
"""

# Stance appended after agent system_prompt when using enriched prompts
_STANCE_SUFFIX = """
## NHIỆM VỤ TRONG CUỘC HỌP (Round 1)
Phát biểu góc nhìn của phòng bạn:
- Phòng bạn quan tâm điều gì trong brief này?
- Cơ hội / rủi ro từ góc độ phòng ban?
- Số liệu Brain liên quan (cite cụ thể)?
- Đề xuất ngắn gọn

Tiếng Việt. Định nghĩa thuật ngữ. Cite Brain mọi nhận định.
KHÔNG dài quá 400 từ — đây là round 1.
"""


class PerspectivesCollector:
    def __init__(
        self,
        departments_root: Path,
        llm,
        max_parallel: int = 5,
        vault_root: Path | None = None,
    ):
        """
        departments_root: path tới thư mục departments (vault/01-Departments hoặc repo/departments).
        vault_root: optional, dùng để tìm agent .md files nếu departments_root không chứa agents/.
                    Nếu None, tìm agent .md ngay trong departments_root/<dept>/agents/.
        """
        self.departments_root = Path(departments_root)
        self.loader = DepartmentLoader(self.departments_root)
        self.agent_loader = AgentLoader()
        self.llm = llm
        self.max_parallel = max_parallel
        # vault_root cho phép tìm agent trong vault khi departments_root là repo path
        self.vault_root = Path(vault_root) if vault_root else None

    def collect(self, state: MeetingState) -> dict:
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            futures = {
                executor.submit(self._speak_dept, dept_code, state): dept_code
                for dept_code in state["departments"]
            }
            for fut in futures:
                dept_code = futures[fut]
                try:
                    results[dept_code] = fut.result()
                except Exception as e:
                    results[dept_code] = f"[ERROR] {e}"

        return {"perspectives": results}

    def _resolve_agent_path(self, dept_code: str, agent_id: str) -> Path | None:
        """Tìm agent .md file. Thử theo thứ tự ưu tiên:
        1. <departments_root>/<dept_code>/agents/<agent_id>.md
        2. <vault_root>/01-Departments/<dept_code>/agents/<agent_id>.md  (nếu vault_root set)
        """
        candidates = [
            self.departments_root / dept_code / "agents" / f"{agent_id}.md",
        ]
        if self.vault_root:
            candidates.append(
                self.vault_root / "01-Departments" / dept_code / "agents" / f"{agent_id}.md"
            )
        for p in candidates:
            if p.exists():
                return p
        return None

    def _speak_dept(self, dept_code: str, state: MeetingState) -> str:
        try:
            dept = self.loader.load(dept_code)
        except FileNotFoundError:
            return f"[Phong {dept_code} chua ton tai trong vault]"

        # P1.1: load enriched agent system_prompt nếu có
        system_prompt = self._load_agent_system_prompt(dept_code, dept)

        agent = BaseAgent(
            name_vn=dept.name_vn,
            role=dept_code,
            system_prompt=system_prompt,
            llm=self.llm,
            department=dept_code,
            temperature=0.5,
        )
        return agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=[],
        )

    def _load_agent_system_prompt(self, dept_code: str, dept) -> str:
        """Load per-agent enriched prompt. Fallback tới generic nếu file missing."""
        speaker = dept.default_speaker
        if not speaker:
            return PERSPECTIVE_PROMPT.format(dept_name=dept.name_vn)

        agent_path = self._resolve_agent_path(dept_code, speaker)
        if agent_path is None:
            # Graceful degradation: file chưa tồn tại
            return PERSPECTIVE_PROMPT.format(dept_name=dept.name_vn)

        try:
            agent_def = self.agent_loader.load(agent_path)
            body = agent_def.system_prompt
            if not body:
                return PERSPECTIVE_PROMPT.format(dept_name=dept.name_vn)
            # Combine: enriched body + stance suffix
            return body + _STANCE_SUFFIX
        except Exception:
            # Bất kỳ lỗi parse nào đều fallback gracefully
            return PERSPECTIVE_PROMPT.format(dept_name=dept.name_vn)
