from datetime import date
from core.obsidian.vault import ObsidianVault


def test_read_brain_file(tmp_path):
    brain = tmp_path / "00-Brain"
    brain.mkdir()
    (brain / "strategy.md").write_text("# Test", encoding="utf-8")

    vault = ObsidianVault(tmp_path)
    assert "Test" in vault.read("00-Brain/strategy.md")


def test_create_task_folder(tmp_path):
    (tmp_path / "02-Tasks").mkdir()
    vault = ObsidianVault(tmp_path)
    folder = vault.create_task_folder("test-slug")
    assert folder.exists()
    assert folder.name.endswith("-test-slug")


def test_write_with_frontmatter(tmp_path):
    vault = ObsidianVault(tmp_path)
    vault.write("test.md", "# Hi", frontmatter={"type": "test"})
    content = (tmp_path / "test.md").read_text(encoding="utf-8")
    assert content.startswith("---\ntype: test\n---\n")
