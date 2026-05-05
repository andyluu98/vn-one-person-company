import pytest
from pathlib import Path
from core.agents.department import Department, DepartmentLoader

REPO = Path(__file__).parent.parent.parent


def test_load_governance_dept():
    loader = DepartmentLoader(REPO / "departments")
    dept = loader.load("01-governance")
    assert dept.code == "01-governance"
    assert dept.name_vn == "Quản trị & Pháp lý"
    assert dept.tier == 1


def test_load_all_returns_12():
    loader = DepartmentLoader(REPO / "departments")
    depts = loader.load_all()
    assert len(depts) == 12


def test_unknown_dept_raises():
    loader = DepartmentLoader(REPO / "departments")
    with pytest.raises(FileNotFoundError):
        loader.load("99-nonexistent")
