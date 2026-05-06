"""Auto-commit vault changes (NEVER push - CEO control)."""
from __future__ import annotations
from pathlib import Path
from typing import Optional


class GitSync:
    def __init__(self, vault_root: Path, enabled: bool = True):
        self.root = Path(vault_root)
        self.enabled = enabled

    def is_repo(self) -> bool:
        return (self.root / ".git").exists()

    def init_if_needed(self) -> None:
        if self.is_repo():
            return
        from git import Repo
        Repo.init(str(self.root))

    def commit(self, message: str, paths: Optional[list[str]] = None) -> Optional[str]:
        if not self.enabled or not self.is_repo():
            return None

        from git import Repo
        repo = Repo(str(self.root))
        if paths:
            repo.index.add(paths)
        else:
            repo.git.add(A=True)

        if not repo.is_dirty(untracked_files=True):
            return None

        commit = repo.index.commit(message)
        return commit.hexsha
