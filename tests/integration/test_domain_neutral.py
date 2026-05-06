"""RULE 2: core/ không được có trade/finance leakage."""
import subprocess
from pathlib import Path
import shutil


def test_no_trade_leakage_in_core():
    repo = Path(__file__).parent.parent.parent
    script = repo / "scripts/dev/check-domain-neutral.sh"

    # On Windows, ensure bash is available; skip if not
    if shutil.which("bash") is None:
        import pytest
        pytest.skip("bash not available on this platform")

    # Use a relative path so Git Bash on Windows can resolve it correctly
    # (bash on Windows can't open scripts via 'F:/...' absolute paths reliably)
    rel_script = "scripts/dev/check-domain-neutral.sh"
    result = subprocess.run(
        ["bash", rel_script],
        cwd=str(repo), capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"Domain-neutral check failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
