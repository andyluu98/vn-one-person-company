"""Resolve template path theo RULE 6:
1. vault/00-Templates-Custom/<dept>/<template>* (CEO custom)
2. vault/01-Departments/<dept>/refs/<template>*
3. repo/templates-vn/<dept>/<template>*
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional


SUPPORTED_EXT = [".md", ".docx", ".xlsx"]


class TemplateResolver:
    def __init__(self, vault_root: Path, repo_templates: Path):
        self.vault = Path(vault_root)
        self.repo = Path(repo_templates)

    def resolve(self, template_name: str, dept_code: str) -> Optional[Path]:
        candidates = [
            self.vault / "00-Templates-Custom" / dept_code,
            self.vault / "01-Departments" / dept_code / "refs",
            self.repo / dept_code,
        ]
        for folder in candidates:
            if not folder.exists():
                continue
            found = self._find_in(folder, template_name)
            if found:
                return found
        return None

    @staticmethod
    def _find_in(folder: Path, name: str) -> Optional[Path]:
        name_lower = name.lower()
        for f in folder.iterdir():
            if not f.is_file():
                continue
            if f.suffix.lower() not in SUPPORTED_EXT:
                continue
            if f.stem.lower().startswith(name_lower) or name_lower in f.stem.lower():
                return f
        return None

    def get_resolution_log(self, template_name: str, dept_code: str) -> dict:
        path = self.resolve(template_name, dept_code)
        if not path:
            return {"found": False, "name": template_name, "dept": dept_code}

        rel = path.resolve()
        if str(rel).startswith(str((self.vault / "00-Templates-Custom").resolve())):
            source = "custom"
        elif str(rel).startswith(str(self.vault.resolve())):
            source = "pack"
        else:
            source = "default"
        return {"found": True, "path": str(rel), "source": source,
                "dept": dept_code, "name": template_name}
