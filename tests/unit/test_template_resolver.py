from pathlib import Path
from core.obsidian.template_resolver import TemplateResolver


def test_priority_custom_first(tmp_path):
    vault = tmp_path / "vault"
    repo = tmp_path / "repo"

    (repo / "templates-vn" / "01-governance").mkdir(parents=True)
    (repo / "templates-vn" / "01-governance" / "noi-quy-lao-dong.md").write_text("DEFAULT", encoding="utf-8")

    (vault / "01-Departments" / "01-governance" / "refs").mkdir(parents=True)
    (vault / "01-Departments" / "01-governance" / "refs" / "noi-quy-lao-dong.md").write_text("PACK", encoding="utf-8")

    (vault / "00-Templates-Custom" / "01-governance").mkdir(parents=True)
    (vault / "00-Templates-Custom" / "01-governance" / "noi-quy-lao-dong.md").write_text("CUSTOM", encoding="utf-8")

    resolver = TemplateResolver(vault_root=vault, repo_templates=repo / "templates-vn")
    path = resolver.resolve("noi-quy-lao-dong", dept_code="01-governance")
    assert path.read_text(encoding="utf-8") == "CUSTOM"


def test_falls_back_to_repo_default(tmp_path):
    vault = tmp_path / "vault"
    repo = tmp_path / "repo"
    (repo / "templates-vn" / "07-marketing").mkdir(parents=True)
    (repo / "templates-vn" / "07-marketing" / "ke-hoach-mkt.md").write_text("DEFAULT", encoding="utf-8")
    vault.mkdir()

    resolver = TemplateResolver(vault_root=vault, repo_templates=repo / "templates-vn")
    path = resolver.resolve("ke-hoach-mkt", dept_code="07-marketing")
    assert "DEFAULT" in path.read_text(encoding="utf-8")


def test_returns_none_when_template_missing(tmp_path):
    resolver = TemplateResolver(vault_root=tmp_path, repo_templates=tmp_path / "fake")
    assert resolver.resolve("xyz", "07-marketing") is None
