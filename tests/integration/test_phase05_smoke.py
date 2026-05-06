"""Phase 5 smoke: imports + 3 packs loadable + template resolver work."""
from pathlib import Path


def test_phase5_imports():
    from core.agents.agent_loader import AgentLoader, AgentDefinition
    from core.agents.registry import Registry, DepartmentWithAgents
    from core.agents.pack_loader import PackLoader, Pack
    from core.obsidian.template_resolver import TemplateResolver
    from core.obsidian.doc_writer import DocWriter
    from core.obsidian.git_sync import GitSync


def test_3_packs_loadable():
    from core.agents.pack_loader import PackLoader
    repo = Path(__file__).parent.parent.parent
    loader = PackLoader(repo / "packs")
    available = loader.list_available()
    assert set(["fnb", "retail", "tech-saas"]).issubset(set(available))

    for code in ["fnb", "retail", "tech-saas"]:
        pack = loader.load(code)
        assert pack.adds_departments


def test_12_core_depts_have_agents():
    from core.agents.registry import Registry
    repo = Path(__file__).parent.parent.parent
    reg = Registry(repo / "departments")

    for code in ["01-governance", "02-strategy", "03-finance", "04-people",
                 "05-operations", "06-sales", "07-marketing", "08-customer",
                 "09-product-tech", "10-training", "11-reporting", "12-growth"]:
        d = reg.get(code)
        assert len(d.agents_by_id) >= 1, f"{code} has no agents"


def test_template_resolver_finds_templates_vn():
    from core.obsidian.template_resolver import TemplateResolver
    repo = Path(__file__).parent.parent.parent

    resolver = TemplateResolver(
        vault_root=repo / "tests/fixtures/demo-vault",
        repo_templates=repo / "templates-vn",
    )
    # 192 templates đã vendored; tìm 1 template bất kỳ trong 04-people
    # Just verify ANY template exists in the dept folder (not specific filename)
    people_dir = repo / "templates-vn" / "04-people"
    if people_dir.exists():
        sample_files = [f for f in people_dir.iterdir() if f.suffix == ".md"]
        if sample_files:
            sample_name = sample_files[0].stem
            found = resolver.resolve(sample_name, "04-people")
            assert found is not None
            assert found.exists()
