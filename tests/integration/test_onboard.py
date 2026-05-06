import subprocess
import sys
from pathlib import Path


def test_onboard_creates_valid_vault(tmp_path):
    repo = Path(__file__).parent.parent.parent
    vault = tmp_path / "test-vault"

    result = subprocess.run(
        [sys.executable, str(repo / "scripts" / "onboard.py"),
         "--vault", str(vault), "--non-interactive"],
        capture_output=True, text=True,
    )

    assert result.returncode == 0, f"Failed: {result.stderr}"

    assert (vault / "00-Brain" / "strategy.md").exists()
    assert (vault / "00-Templates-Custom" / "README.md").exists()
    assert (vault / "01-Departments").exists()
    assert (vault / "02-Tasks").exists()
    assert (vault / ".vncoderc").exists()
    assert (vault / ".git").exists()


def test_onboard_with_pack_installs_dept(tmp_path):
    repo = Path(__file__).parent.parent.parent
    vault = tmp_path / "v2"

    subprocess.run(
        [sys.executable, str(repo / "scripts" / "onboard.py"),
         "--vault", str(vault), "--non-interactive"],
        capture_output=True, text=True,
    )

    sys.path.insert(0, str(repo))
    from scripts.onboard import _install_pack
    _install_pack(repo / "packs" / "fnb", vault)

    assert (vault / "01-Departments" / "13-kitchen").exists()
