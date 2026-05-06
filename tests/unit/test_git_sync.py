from pathlib import Path
from core.obsidian.git_sync import GitSync


def test_init_and_commit(tmp_path):
    sync = GitSync(tmp_path)
    sync.init_if_needed()

    (tmp_path / "test.md").write_text("hello", encoding="utf-8")
    sha = sync.commit("test: add file")
    assert sha is not None
    assert len(sha) == 40


def test_no_commit_when_clean(tmp_path):
    sync = GitSync(tmp_path)
    sync.init_if_needed()
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    sync.commit("first")

    sha2 = sync.commit("second (no changes)")
    assert sha2 is None
