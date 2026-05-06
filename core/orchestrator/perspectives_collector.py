"""Round 1 — moi phong phat bieu goc nhin (parallel)."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from core.agents.department import DepartmentLoader
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


class PerspectivesCollector:
    def __init__(self, departments_root: Path, llm, max_parallel: int = 5):
        self.loader = DepartmentLoader(departments_root)
        self.llm = llm
        self.max_parallel = max_parallel

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

    def _speak_dept(self, dept_code: str, state: MeetingState) -> str:
        try:
            dept = self.loader.load(dept_code)
        except FileNotFoundError:
            return f"[Phong {dept_code} chua ton tai trong vault]"

        agent = BaseAgent(
            name_vn=dept.name_vn,
            role=dept_code,
            system_prompt=PERSPECTIVE_PROMPT.format(dept_name=dept.name_vn),
            llm=self.llm,
            department=dept_code,
            temperature=0.5,
        )
        return agent.speak(
            brief=state["brief"],
            brain_context=state["brain_context"],
            history=[],
        )
