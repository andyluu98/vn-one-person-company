"""Obsidian vault I/O wrapper."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import yaml


class ObsidianVault:
    def __init__(self, root: Path):
        self.root = Path(root)

    def read(self, rel_path: str) -> str:
        return (self.root / rel_path).read_text(encoding="utf-8")

    def write(self, rel_path: str, content: str, frontmatter: dict | None = None) -> None:
        full = self.root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        out = ""
        if frontmatter:
            out = "---\n" + yaml.safe_dump(
                frontmatter,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=True,
            ) + "---\n"
        out += content
        full.write_text(out, encoding="utf-8")

    def create_task_folder(self, slug: str) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d-%H%M")
        folder = self.root / "02-Tasks" / f"{ts}-{slug}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def list_tasks(self) -> list[Path]:
        tasks_dir = self.root / "02-Tasks"
        if not tasks_dir.exists():
            return []
        return sorted([p for p in tasks_dir.iterdir() if p.is_dir()])
