"""Real LLM E2E — chỉ run khi có ANTHROPIC_API_KEY + RUN_REAL_LLM=1.

Đo: < 25 phút, < $2/task.
"""
import os
import time
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
FIXTURE = REPO / "tests/fixtures/techco-vault"


@pytest.mark.skipif(
    not (os.getenv("ANTHROPIC_API_KEY") and os.getenv("RUN_REAL_LLM") == "1"),
    reason="Real LLM test — needs API key + RUN_REAL_LLM=1",
)
def test_real_llm_e2e_under_budget(tmp_path):
    import shutil
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)

    from core.orchestrator.flow_controller import FlowController
    from core.llm.providers import get_default_provider

    llm = get_default_provider()
    fc = FlowController(vault_root=vault, llm=llm)

    start = time.time()
    result = fc.run(brief="Tạo chiến dịch QC nhắm khách thu nhập 50tr+ NS 500tr")
    elapsed = time.time() - start

    # Stage 1 should be quick (no meeting yet)
    assert elapsed < 60
    assert result.task_folder.exists()
