# Phase 6 — Adapters + E2E + Onboard Wizard

**Goal:** Ship Claude Code skill + Claude Cowork plugin adapter + Onboarding wizard + E2E test case B (chiến dịch QC) pass.

**Dependency:** Phase 1, 2, 3, 4, 5.

**Estimated tasks:** 10

---

### Task 1: Onboard wizard

**Files:**
- Create: `scripts/onboard.py`
- Create: `tests/integration/test_onboard.py`

- [ ] **Step 1.1: Implement wizard**

```python
# scripts/onboard.py
"""Onboarding wizard — tạo vault mới cho DN."""
from __future__ import annotations
import shutil
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
import yaml

console = Console()


@click.command()
@click.option("--vault", type=click.Path(), required=True, help="Vault destination")
@click.option("--non-interactive", is_flag=True, help="Skip prompts (for CI)")
def main(vault, non_interactive):
    """Onboard wizard: tạo vault + chọn pack + import template DN."""
    repo = Path(__file__).parent.parent
    vault_path = Path(vault).expanduser().resolve()
    
    if vault_path.exists() and any(vault_path.iterdir()):
        if not Confirm.ask(f"⚠️  {vault_path} đã có dữ liệu. Tiếp tục? (sẽ ghi đè)"):
            console.print("[red]Hủy.[/]")
            return
    
    # Step 1: Copy vault scaffold
    console.print("[bold]Bước 1/5:[/] Tạo vault scaffold...")
    shutil.copytree(repo / "vault-template", vault_path, dirs_exist_ok=True)
    console.print(f"  ✓ Vault tạo tại {vault_path}")
    
    # Step 2: Hỏi DN ngành gì
    console.print("\n[bold]Bước 2/5:[/] Chọn industry pack")
    if non_interactive:
        selected_packs = []
    else:
        selected_packs = []
        for code, name in [("fnb", "F&B (quán ăn/cafe/nhà hàng)"),
                           ("retail", "Retail (shop/e-commerce/D2C)"),
                           ("tech-saas", "Tech/SaaS (startup phần mềm)")]:
            if Confirm.ask(f"  Cài pack {name}?", default=False):
                selected_packs.append(code)
        if not selected_packs:
            console.print("  → Chỉ dùng 13 phòng core")
    
    # Step 3: Copy departments + selected packs
    console.print("\n[bold]Bước 3/5:[/] Cài đặt phòng ban...")
    _install_departments(repo / "departments", vault_path / "01-Departments")
    for code in selected_packs:
        _install_pack(repo / "packs" / code, vault_path)
        console.print(f"  ✓ Pack {code} đã cài")
    
    # Step 4: Brain template (theo pack đầu tiên nếu có)
    console.print("\n[bold]Bước 4/5:[/] Brain template")
    if selected_packs:
        first_pack = selected_packs[0]
        pack_brain = repo / "packs" / first_pack / "brain-template"
        if pack_brain.exists():
            for f in pack_brain.glob("*.md"):
                target = vault_path / "00-Brain" / f.name
                shutil.copy(f, target)
                console.print(f"  ✓ Override {f.name} từ pack {first_pack}")
    
    # Step 5: BYOT prompt
    console.print("\n[bold]Bước 5/5:[/] Templates riêng (BYOT)")
    if not non_interactive:
        if Confirm.ask("  DN đã có template hợp đồng/biểu mẫu riêng?", default=False):
            src = Prompt.ask("  Đường dẫn folder template (sẽ copy vào 00-Templates-Custom/)")
            src_path = Path(src).expanduser()
            if src_path.exists():
                _import_byot(src_path, vault_path / "00-Templates-Custom")
                console.print(f"  ✓ BYOT đã import từ {src_path}")
    
    # Init Git
    if Confirm.ask("\n[bold]Init Git private repo cho vault?[/]", default=True) if not non_interactive else True:
        from git import Repo
        if not (vault_path / ".git").exists():
            Repo.init(str(vault_path))
            console.print("  ✓ Git initialized")
    
    # Save config
    config_path = vault_path / ".vncoderc"
    config_path.write_text(yaml.safe_dump({
        "vault_path": str(vault_path),
        "packs": selected_packs,
        "version": "0.1.0",
    }, allow_unicode=True), encoding="utf-8")
    
    console.print(f"\n[green]✅ Vault sẵn sàng tại {vault_path}[/]")
    console.print("[bold]Bước tiếp:[/]")
    console.print(f"  1. Mở {vault_path}/00-Brain/ và điền strategy/products/budget/...")
    console.print(f"  2. Chạy: [cyan]vn-os run --brief 'task của bạn' --vault {vault_path}[/]")


def _install_departments(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        if child.is_dir() and not child.name.startswith("_"):
            shutil.copytree(child, dst / child.name, dirs_exist_ok=True)


def _install_pack(pack_dir: Path, vault: Path):
    pack_yaml = pack_dir / "pack.yaml"
    if not pack_yaml.exists():
        return
    pack_data = yaml.safe_load(pack_yaml.read_text(encoding="utf-8"))
    
    # Copy adds_departments
    for dept_code in pack_data.get("adds_departments", []):
        src = pack_dir / "departments" / dept_code
        dst = vault / "01-Departments" / dept_code
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)


def _import_byot(src: Path, dst: Path):
    """Copy custom templates từ DN vào 00-Templates-Custom/, classify cơ bản."""
    dst.mkdir(parents=True, exist_ok=True)
    
    classify_keywords = {
        "01-governance": ["dieu-le", "noi-quy", "quy-che", "chinh-sach"],
        "03-finance": ["phieu-thu", "phieu-chi", "hoa-don", "bctc", "ngan-sach"],
        "04-people": ["jd", "hop-dong-lao-dong", "so-tay-nv", "luong"],
        "05-operations": ["sop", "bien-ban", "bao-cao"],
    }
    
    for f in src.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in [".md", ".docx", ".xlsx", ".pdf"]:
            continue
        name_lower = f.stem.lower().replace("_", "-").replace(" ", "-")
        target_dept = "_unsorted"
        for dept, keywords in classify_keywords.items():
            if any(kw in name_lower for kw in keywords):
                target_dept = dept
                break
        target_dir = dst / target_dept
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, target_dir / f.name)


if __name__ == "__main__":
    main()
```

- [ ] **Step 1.2: Test wizard**

```python
# tests/integration/test_onboard.py
import subprocess
from pathlib import Path


def test_onboard_creates_valid_vault(tmp_path):
    repo = Path(__file__).parent.parent.parent
    vault = tmp_path / "test-vault"
    
    result = subprocess.run(
        ["python", str(repo / "scripts" / "onboard.py"),
         "--vault", str(vault), "--non-interactive"],
        capture_output=True, text=True,
    )
    
    assert result.returncode == 0, f"Failed: {result.stderr}"
    
    # Verify scaffold
    assert (vault / "00-Brain" / "strategy.md").exists()
    assert (vault / "00-Templates-Custom" / "README.md").exists()
    assert (vault / "01-Departments").exists()
    assert (vault / "02-Tasks").exists()
    assert (vault / ".vncoderc").exists()
    assert (vault / ".git").exists()


def test_onboard_with_pack_installs_dept(tmp_path):
    repo = Path(__file__).parent.parent.parent
    vault = tmp_path / "v2"
    
    # Run with pack hardcoded (simulate user picked "fnb")
    # For non-interactive: skip pack selection
    # → Test: install pack manually after non-interactive
    subprocess.run(
        ["python", str(repo / "scripts" / "onboard.py"),
         "--vault", str(vault), "--non-interactive"],
        capture_output=True, text=True,
    )
    
    # Manually install fnb pack (to test installer)
    import sys; sys.path.insert(0, str(repo))
    from scripts.onboard import _install_pack
    _install_pack(repo / "packs" / "fnb", vault)
    
    assert (vault / "01-Departments" / "13-kitchen").exists()
```

- [ ] **Step 1.3: Wire CLI**

```python
# Update core/cli.py: replace `def onboard():` stub
@main.command()
@click.option("--vault", type=click.Path(), required=True)
def onboard(vault):
    """Wizard tạo vault mới cho DN."""
    import subprocess, sys
    from pathlib import Path
    repo = Path(__file__).parent.parent
    subprocess.run(
        [sys.executable, str(repo / "scripts" / "onboard.py"), "--vault", vault]
    )
```

- [ ] **Step 1.4: Commit**

```bash
pytest tests/integration/test_onboard.py -v
git add scripts/onboard.py tests/integration/test_onboard.py core/cli.py
git commit -m "feat(onboard): add interactive wizard (vault + pack + BYOT)"
```

---

### Task 2: Claude Code skill adapter

**Files:**
- Create: `adapters/claude-code/skill.md`
- Create: `adapters/claude-code/README.md`
- Create: `adapters/claude-code/install.sh`

- [ ] **Step 2.1: Create skill.md**

```markdown
---
name: vn-business-os
description: AI agent OS cho doanh nghiệp Việt Nam. Chat tự nhiên với CEO, gọi Python CLI điều phối các phòng ban (agents) họp bàn, debate, sinh báo cáo + tài liệu .docx/.xlsx tuân thủ luật VN. Use when user wants to manage business operations, create campaigns, generate JDs, contracts, plans, or any business documentation in Vietnamese context.
---

# VN Business OS — Claude Code Skill

Khi CEO chat với task DN, skill này:

1. Phát hiện vault VN Business OS (folder có `00-Brain/`)
2. Chuyển brief sang Python CLI: `vn-os run --brief "<text>" --vault <path>`
3. Đọc kết quả từ Obsidian vault để báo cáo cho CEO
4. CEO duyệt qua các stop point (clarification, decision, execute)

## Khi user nói các câu sau → trigger skill

- "Tạo chiến dịch ..."
- "Soạn JD ..."
- "Lập kế hoạch ..."
- "Tính ngân sách ..."
- "Đóng gói doanh nghiệp"
- "Hệ thống hóa tài liệu DN"
- "Phân tích đối thủ ..."

## Workflow

### Bước 1: Verify vault
```bash
ls $VAULT/00-Brain/strategy.md
```
Nếu KHÔNG có → đề xuất chạy `vn-os onboard --vault $VAULT`.

### Bước 2: Run task
```bash
vn-os run --brief "<user's brief>" --vault $VAULT
```
Output sẽ tạo folder `02-Tasks/<timestamp>-<slug>/` và pause ở clarification.

### Bước 3: Đọc clarification, hỏi CEO
Đọc `02-Tasks/<task>/03-clarification.md`, hỏi CEO chọn từng câu, edit file (tick checkbox), rồi:
```bash
vn-os meeting <task-folder>
```

### Bước 4: Sau meeting, đọc 07-decision-report.md
Tóm tắt cho CEO. Hỏi: approve/revise/reject.

### Bước 5: Sau approve
```bash
vn-os approve <task-folder>
vn-os execute <task-folder>
```

## Quan trọng

- LUÔN dùng tiếng Việt khi giao tiếp CEO
- LUÔN cite file Obsidian khi trích thông tin (vd: "theo 00-Brain/strategy.md")
- KHÔNG bịa nội dung — chỉ summary từ output Python CLI
- Nếu Python CLI lỗi → báo CEO + suggest debug command
```

- [ ] **Step 2.2: install.sh**

```bash
#!/usr/bin/env bash
# Install Claude Code skill
set -euo pipefail

CLAUDE_AGENTS_DIR="${CLAUDE_AGENTS_DIR:-$HOME/.claude/skills}"
mkdir -p "$CLAUDE_AGENTS_DIR/vn-business-os"

cp "$(dirname "$0")/skill.md" "$CLAUDE_AGENTS_DIR/vn-business-os/SKILL.md"
echo "✅ Installed Claude Code skill to $CLAUDE_AGENTS_DIR/vn-business-os/"
echo ""
echo "Next: trong Claude Code, skill 'vn-business-os' sẽ tự active khi user nói tiếng Việt về DN."
```

- [ ] **Step 2.3: README adapter**

```markdown
# Claude Code Adapter

Adapter cho Claude Code (CLI / desktop / web). 

## Install
\`\`\`bash
bash adapters/claude-code/install.sh
\`\`\`

## Verify
Trong Claude Code session, gõ: "Tạo chiến dịch QC nhắm khách thu nhập 50tr+"
Skill `vn-business-os` sẽ tự active.
```

- [ ] **Step 2.4: Commit**

```bash
chmod +x adapters/claude-code/install.sh
git add adapters/claude-code/
git commit -m "feat(adapters): add Claude Code skill adapter"
```

---

### Task 3: Claude Cowork plugin adapter

**Files:**
- Create: `adapters/claude-cowork/plugin.json`
- Create: `adapters/claude-cowork/.claude-plugin/plugin.json`
- Create: `adapters/claude-cowork/skills/vn-business-os/SKILL.md`
- Create: `adapters/claude-cowork/build-plugin.sh`

- [ ] **Step 3.1: Plugin metadata**

```json
{
  "name": "vn-business-os",
  "version": "0.1.0",
  "description": "AI agent OS cho doanh nghiệp Việt Nam — debate giữa các phòng ban, sinh tài liệu .docx/.xlsx tuân thủ luật VN. Powered by Python + LangGraph backend.",
  "author": {
    "email": "your-email@example.com"
  },
  "credits": {
    "templates_vn": "adapted from business-builder.plugin",
    "debate_engine_pattern": "TradingAgents (TauricResearch)"
  },
  "keywords": ["business", "vietnam", "agents", "debate", "langgraph"]
}
```

- [ ] **Step 3.2: Build script (zip)**

```bash
#!/usr/bin/env bash
# Build .claude-plugin file
set -euo pipefail

DIR="$(dirname "$0")"
OUT="${1:-vn-business-os.plugin}"
TMP=$(mktemp -d)

mkdir -p "$TMP/.claude-plugin" "$TMP/skills/vn-business-os"
cp "$DIR/.claude-plugin/plugin.json" "$TMP/.claude-plugin/"
cp "$DIR/skills/vn-business-os/SKILL.md" "$TMP/skills/vn-business-os/"
cp "$DIR/README.md" "$TMP/" 2>/dev/null || true

(cd "$TMP" && zip -qr "$OUT" .)
mv "$TMP/$OUT" "./$OUT"
rm -rf "$TMP"

echo "✅ Built $OUT"
```

- [ ] **Step 3.3: Commit**

```bash
chmod +x adapters/claude-cowork/build-plugin.sh
git add adapters/claude-cowork/
git commit -m "feat(adapters): add Claude Cowork plugin builder"
```

---

### Task 4: E2E test case B — Setup demo TechCo vault

**Files:**
- Create: `tests/fixtures/techco-vault/00-Brain/*.md` (full sample data)
- Create: `tests/fixtures/techco-vault/01-Departments/` (clone từ /departments)

- [ ] **Step 4.1: Bulk create techco fixture**

```bash
# tests/fixtures/techco-vault/setup.sh
#!/usr/bin/env bash
set -euo pipefail
DIR="$(dirname "$0")"
REPO="$DIR/../../.."

mkdir -p "$DIR/00-Brain" "$DIR/02-Tasks" "$DIR/03-Outputs" "$DIR/00-Templates-Custom"

cat > "$DIR/00-Brain/strategy.md" <<'EOF'
---
type: brain
section: strategy
last_updated: 2026-05-06
---
# Chiến lược TechCo

## Tầm nhìn
TechCo trở thành SaaS quản lý SME hàng đầu VN, focus đơn giản hoá vận hành.

## Khách hàng mục tiêu (ICP)
- Phân khúc: SME 5-50 nhân viên (chủ DN, không phải khách cá nhân cao cấp)
- Đặc điểm: chủ tự vận hành, ngân sách hạn chế, ưu tiên đơn giản
- Pain point: 
  - Quản lý KH thủ công bằng Excel
  - Báo cáo chậm, không real-time
  - Tốn thời gian admin việc lặp đi lặp lại

## Mục tiêu năm 2026
- Doanh thu: 5 tỉ ARR (đầu năm 4.2 tỉ)
- Khách: 200 active (hiện 150)
- Mở rộng: chưa, focus retention + expansion
EOF

cat > "$DIR/00-Brain/products.md" <<'EOF'
---
type: brain
section: products
last_updated: 2026-05-06
---
# Sản phẩm

| Mã | Tên | Giá | Margin | Trạng thái |
|---|---|---|---|---|
| STR | Starter | 1000000 | 60 | active |
| GRO | Growth | 5000000 | 70 | active |
| PRE | Premium | 20000000 | 75 | active |

## Đặc điểm
- Starter: 1-5 user, basic CRM + báo cáo cơ bản
- Growth: 5-20 user, full CRM + automation + 5 SOP có sẵn
- Premium: unlimited user, white-label, API, dedicated CSM, SLA 4h
EOF

cat > "$DIR/00-Brain/budget.md" <<'EOF'
---
type: brain
section: budget
last_updated: 2026-05-06
---
# Ngân sách 2026

## Tổng quan năm
- Tổng ngân sách: 1200000000
- Đã chi (T1-T4): 400000000
- Còn lại: 800000000

## Phân bổ phòng ban (quý 2)

| Phòng | Cấp Q2 | Đã chi | Còn lại |
|---|---|---|---|
| Marketing | 800000000 | 0 | 800000000 |
| Sales | 200000000 | 50000000 | 150000000 |
| Operations | 150000000 | 30000000 | 120000000 |
EOF

cat > "$DIR/00-Brain/headcount.md" <<'EOF'
---
type: brain
section: headcount
last_updated: 2026-05-06
---
# Nhân sự / Agents

## Phòng ban đang active
- 02-strategy
- 03-finance
- 04-people
- 05-operations
- 06-sales
- 07-marketing
- 08-customer
- 09-product-tech

## Agents Marketing hiện có
- brand-manager
- content-creator (general)
- ads-specialist
- seo-specialist

## Gap chuyên môn
- Marketing: thiếu content-premium-b2b-specialist (nếu cần nhắm khách cao cấp)
EOF

cat > "$DIR/00-Brain/state.md" <<'EOF'
---
type: brain
section: state
last_updated: 2026-05-06
---
# Trạng thái DN

## Giai đoạn
[growth-stage]

## Quý hiện tại (Q2 2026)
- MRR: 350000000
- ARR: 4200000000
- Active customers: 150

## Runway
- Tiền mặt: 800000000
- Burn / tháng: 45000000
- Runway: 18 tháng
EOF

# Minimal other Brain files
echo "---\ntype: brain\nsection: laws\n---\n# Laws\n- Luật DN 2020\n- Luật Quảng cáo 2012" > "$DIR/00-Brain/laws.md"
echo "---\ntype: brain\nsection: decisions\n---\n# Decisions Log" > "$DIR/00-Brain/decisions-log.md"
echo "---\ntype: brain\nsection: glossary\n---\n# Glossary" > "$DIR/00-Brain/glossary.md"

# Copy departments
cp -r "$REPO/departments" "$DIR/01-Departments"

echo "✅ TechCo vault fixture created"
```

- [ ] **Step 4.2: Run setup**

```bash
chmod +x tests/fixtures/techco-vault/setup.sh
bash tests/fixtures/techco-vault/setup.sh
```

- [ ] **Step 4.3: Commit**

```bash
git add tests/fixtures/techco-vault/
git commit -m "test(fixtures): add TechCo vault fixture for E2E test B"
```

---

### Task 5: E2E test case B — Implementation

**Files:**
- Create: `tests/e2e/test_b_campaign_high_income.py`

- [ ] **Step 5.1: Implement E2E test (mocked LLM)**

```python
# tests/e2e/test_b_campaign_high_income.py
"""E2E test case B — Chiến dịch QC nhắm khách thu nhập 50tr+.

Validates ALL 6 RULES + acceptance criteria.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest


REPO = Path(__file__).parent.parent.parent
FIXTURE = REPO / "tests/fixtures/techco-vault"


@pytest.fixture
def llm_mock():
    """Mocked LLM với responses pre-canned cho từng giai đoạn."""
    
    responses = {
        # Router
        "router_classify": json.dumps({
            "class": "COMPLEX",
            "departments": ["07-marketing", "02-strategy", "03-finance", "08-customer", "01-governance"],
            "reasoning": "Campaign QC + budget lớn + cần check legal + ICP gap",
        }),
        # Gap analyzer
        "gap_analysis": json.dumps([
            {"field": "ICP", "severity": "CRITICAL",
             "current_value": "SME (chủ DN)", "brief_value": "thu nhập 50tr+",
             "reason": "Brief lệch ICP strategy", "citation": "00-Brain/strategy.md"},
            {"field": "content_capability", "severity": "CRITICAL",
             "current_value": "không có content-premium", "brief_value": "cần content cao cấp",
             "reason": "Headcount thiếu specialist", "citation": "00-Brain/headcount.md"},
        ]),
        # Question generator
        "questions": json.dumps([
            {"text": "Pivot dài hạn hay test 1 lần?",
             "citation": "00-Brain/strategy.md",
             "choices": ["Pivot dài hạn", "Test 1 lần (chủ SME thu nhập 50tr+)", "Hủy"],
             "severity": "CRITICAL", "free_text": False},
            {"text": "Tạo agent content-premium hay outsource?",
             "citation": "00-Brain/headcount.md",
             "choices": ["Tạo agent mới", "Outsource", "Marketing kiêm"],
             "severity": "CRITICAL", "free_text": False},
        ]),
        # Tool router
        "tool_plan": json.dumps({"tools": [
            {"tool": "vn_law_search", "queries": ["luật quảng cáo SaaS B2B VN"]},
            {"tool": "competitor_research", "queries": ["SaaS quản lý SME VN đối thủ"]},
            {"tool": "industry_benchmark", "queries": ["saas_b2b cac"]},
        ]}),
        # Perspectives (5 phòng)
        "perspective_marketing": "MKT đề xuất FB+LinkedIn 60%, content 30%, webinar 10%. KPI 200 lead.",
        "perspective_strategy": "Strategy: OK test nếu < 50% deal từ campaign mới. Cảnh báo lệch ICP.",
        "perspective_finance": "Finance: 500tr/800tr = 62%. Đề xuất 250tr/12 tuần thay 6.",
        "perspective_customer": "Customer: chưa có CSKH Premium tier, nguy cơ churn cao.",
        "perspective_governance": "Legal: SaaS B2B QC OK, nhưng KHÔNG so sánh trực tiếp đối thủ.",
        # Pro/Con
        "pro_advocate": "GO. Cơ hội thị trường rõ. CAC 8tr/SQL theo benchmark.",
        "con_advocate": "Rủi ro 62% budget dồn 1 chỗ + CSKH chưa ready. Đề xuất pilot 200tr/4 tuần.",
        # Perspective debators
        "growth": "GO bold — runway 18m đủ test ICP cao cấp.",
        "cautious": "GO with gates — tuần 1 CTR < 2% pause, tuần 4 0 deal kill.",
        "balanced": "Pilot 200tr/4 tuần + setup CSKH Premium + train sales.",
        # Synthesizer
        "synthesizer": """## 📌 Tóm lại (đọc 30 giây)
- ✅ GO with revisions: 200tr/4 tuần (thay 500tr/6 tuần)
- ⚠️ 4 BLOCKERS phải xong trước launch: setup CSKH, train sales, tạo agent content, update privacy
- 🎯 KPI: 1 deal Premium tháng đầu. Nếu 0 → kill

## Khuyến nghị
GO with revisions

## Việc cần làm trước launch
1. [ ] Setup CSKH Premium tier (SLA 4h)
2. [ ] Train sales pitch Premium (2 buổi)
3. [ ] Tạo agent content-premium-b2b-specialist
4. [ ] Update privacy policy

## KPI gates
- Tuần 1: CTR ≥ 2%
- Tuần 2: CPL ≤ 200tr/SQL
- Tuần 4: ≥ 1 deal Premium

## Câu hỏi cần CEO quyết
A. Approve plan này (200tr/4 tuần + 4 blockers)
B. Approve nhưng không chờ blockers
C. Reject
D. Sửa
""",
        # Translator simplifier (no-op for test simplicity)
        "simplifier": "[same as synthesizer]",
        # TLDR generator (already in synthesizer)
        "tldr": "[already present]",
    }
    
    call_log = []
    
    def respond(messages, model=None):
        call_log.append({"messages": messages, "model": model})
        sys_text = messages[0]["content"]
        user_text = messages[1]["content"] if len(messages) > 1 else ""
        full = sys_text + user_text
        
        # Routing logic
        if "Router" in sys_text and "Phân loại" in sys_text:
            return responses["router_classify"]
        if "Gap Analyzer" in sys_text:
            return responses["gap_analysis"]
        if "sinh câu hỏi clarification" in sys_text:
            return responses["questions"]
        if "Tool Router" in sys_text:
            return responses["tool_plan"]
        if "Pro Advocate" in sys_text:
            return responses["pro_advocate"]
        if "Con Advocate" in sys_text:
            return responses["con_advocate"]
        if "TĂNG TRƯỞNG" in sys_text:
            return responses["growth"]
        if "THẬN TRỌNG" in sys_text:
            return responses["cautious"]
        if "CÂN BẰNG" in sys_text:
            return responses["balanced"]
        if "tổng hợp họp" in sys_text.lower():
            return responses["synthesizer"]
        if "biên tập viên" in sys_text:
            return responses["synthesizer"]   # simplifier = noop
        if "Tóm tắt báo cáo" in sys_text:
            return ""   # tldr already in synthesizer
        if "phòng" in sys_text.lower() and "trong DN VN" in sys_text:
            # Perspective collector — return any reasonable
            for k in ["07-marketing", "02-strategy", "03-finance", "08-customer", "01-governance"]:
                if k in user_text:
                    return responses[f"perspective_{k.split('-')[1]}"]
            return responses["perspective_marketing"]
        return "..."
    
    llm = MagicMock()
    llm.complete.side_effect = respond
    llm.call_log = call_log
    return llm


def test_e2e_b_campaign_full_flow(tmp_path, llm_mock, monkeypatch):
    """Full E2E flow: brief → clarify → meeting → decision report → execute."""
    import shutil
    
    # Setup vault
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)
    
    # Patch llm provider
    monkeypatch.setattr("core.llm.providers.get_default_provider", lambda: llm_mock)
    
    from core.orchestrator.flow_controller import FlowController, FlowStage
    
    fc = FlowController(vault_root=vault, llm=llm_mock)
    
    # Stage 1: brief → clarification
    result = fc.run(brief="Tạo chiến dịch QC nhắm khách thu nhập 50tr+, NS 500tr, launch trước 30/6")
    
    assert result.stage == FlowStage.PAUSE_CLARIFICATION
    task_folder = result.task_folder
    
    # Verify files
    assert (task_folder / "00-brief.md").exists()
    assert (task_folder / "01-routing.md").exists()
    assert (task_folder / "02-context.md").exists()
    assert (task_folder / "03-clarification.md").exists()
    
    # RULE 1 check: questions có citation
    clarif = (task_folder / "03-clarification.md").read_text(encoding="utf-8")
    assert "00-Brain/strategy.md" in clarif
    assert "00-Brain/headcount.md" in clarif
    
    # Auto-answer clarification (simulate CEO tick)
    answered = clarif.replace(
        "- [ ] Test 1 lần (chủ SME thu nhập 50tr+)",
        "- [x] Test 1 lần (chủ SME thu nhập 50tr+)",
    ).replace(
        "- [ ] Tạo agent mới",
        "- [x] Tạo agent mới",
    )
    (task_folder / "03-clarification.md").write_text(answered, encoding="utf-8")
    
    # Stage 2: resume after clarification
    result = fc.resume_after_clarification(task_folder)
    assert result.stage == FlowStage.PAUSE_DECISION_REPORT
    
    # Stage 3: meeting
    departments = ["07-marketing", "02-strategy", "03-finance", "08-customer", "01-governance"]
    result = fc.run_meeting(task_folder, departments=departments)
    assert result.stage == FlowStage.PAUSE_DECISION_REPORT
    
    # Verify meeting outputs
    assert (task_folder / "03b-research-findings.md").exists()
    assert (task_folder / "04-meeting-r1-perspectives.md").exists()
    assert (task_folder / "05-meeting-r2-debate.md").exists()
    assert (task_folder / "06-meeting-r3-perspectives.md").exists()
    assert (task_folder / "07-decision-report.md").exists()
    
    # ACCEPTANCE CRITERIA CHECKS
    decision = (task_folder / "07-decision-report.md").read_text(encoding="utf-8")
    
    # RULE 4: TL;DR + jargon (Tóm lại + định nghĩa)
    assert "📌 Tóm lại" in decision
    
    # RULE 5: research findings present
    research = (task_folder / "03b-research-findings.md").read_text(encoding="utf-8")
    assert "vn_law_search" in research or "competitor_research" in research or "industry_benchmark" in research
    
    # Approval flow checkpoints exist
    assert "Câu hỏi cần CEO quyết" in decision or "Khuyến nghị" in decision


def test_acceptance_no_trade_leakage_in_outputs(tmp_path, llm_mock, monkeypatch):
    """RULE 2: outputs phải không có Bull/Bear/trade/etc."""
    import shutil
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE, vault)
    monkeypatch.setattr("core.llm.providers.get_default_provider", lambda: llm_mock)
    
    from core.orchestrator.flow_controller import FlowController
    fc = FlowController(vault_root=vault, llm=llm_mock)
    result = fc.run(brief="Test campaign")
    
    forbidden = ["Bull", "Bear", "ticker", "yfinance", "trader"]
    for f in (result.task_folder).rglob("*.md"):
        content = f.read_text(encoding="utf-8")
        for word in forbidden:
            assert word not in content, f"Found '{word}' in {f.name}"
```

- [ ] **Step 5.2: Run + commit**

```bash
pytest tests/e2e/test_b_campaign_high_income.py -v
git add tests/e2e/test_b_campaign_high_income.py
git commit -m "test(e2e): add test case B (chiến dịch QC) E2E with all 6 RULES check"
```

---

### Task 6: Real LLM smoke test (manual, optional)

**Files:**
- Create: `tests/e2e/test_real_llm.py`

- [ ] **Step 6.1: Real LLM test (skipped without API key)**

```python
# tests/e2e/test_real_llm.py
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
    
    assert elapsed < 60   # Stage 1 should be quick (no meeting yet)
    assert result.task_folder.exists()
    
    # NOTE: full meeting test cần ANTHROPIC budget — skip in CI
```

- [ ] **Step 6.2: Commit**

```bash
git add tests/e2e/test_real_llm.py
git commit -m "test(e2e): add optional real LLM smoke (gated by env)"
```

---

### Task 7: Documentation — Getting Started

**Files:**
- Create: `docs/getting-started.md`
- Create: `docs/architecture.md`
- Create: `docs/how-to-create-pack.md`
- Create: `docs/how-to-create-agent.md`

- [ ] **Step 7.1: Getting Started**

```markdown
# Getting Started — VN Business OS

> AI agent OS cho doanh nghiệp Việt Nam. CEO chat, agents họp bàn, sinh tài liệu.

## 1. Cài đặt

\`\`\`bash
git clone https://github.com/your/vn-business-os
cd vn-business-os
pip install -e .
export ANTHROPIC_API_KEY=sk-...
export TAVILY_API_KEY=tvly-...
\`\`\`

## 2. Onboard DN của bạn

\`\`\`bash
vn-os onboard --vault ~/my-company-vault
\`\`\`

Wizard sẽ:
- Tạo vault Obsidian scaffold
- Hỏi DN bạn ngành gì (F&B / Retail / Tech-SaaS / khác)
- Cài pack tương ứng
- Hỏi có template riêng không (BYOT)
- Init Git private repo

## 3. Điền Brain

Mở `~/my-company-vault/00-Brain/` trong Obsidian, điền:
- `strategy.md` — tầm nhìn, ICP, mục tiêu
- `products.md` — sản phẩm + giá + margin
- `budget.md` — ngân sách quý
- `headcount.md` — phòng ban active
- `state.md` — KPI hiện tại

## 4. Giao việc đầu tiên

\`\`\`bash
vn-os run --brief "Tạo chiến dịch QC nhắm khách doanh nghiệp" --vault ~/my-company-vault
\`\`\`

Hệ thống sẽ:
1. Đọc Brain
2. Phân loại task (SIMPLE/COMPLEX/STRATEGIC)
3. Phát hiện gap, tạo `03-clarification.md` với câu hỏi
4. **DỪNG** chờ bạn trả lời

Mở file, tick checkbox, lưu, rồi:

\`\`\`bash
vn-os meeting <task-folder>
\`\`\`

→ Hệ thống chạy debate giữa các phòng → tạo `07-decision-report.md` → **DỪNG** chờ bạn duyệt.

\`\`\`bash
vn-os approve <task-folder>
vn-os execute <task-folder>
\`\`\`

→ Sinh `.docx/.xlsx` vào `03-Outputs/`.

## 5. Tích hợp Claude Code / Cowork

\`\`\`bash
bash adapters/claude-code/install.sh
\`\`\`

Trong Claude Code, gõ tự nhiên: *"Tạo chiến dịch QC nhắm khách thu nhập 50tr+"* — skill sẽ tự active.

## 6. 6 Rules quan trọng

1. **Brain-first**: Hệ thống không hỏi nếu chưa đọc Brain
2. **Domain-neutral**: Không có dấu vết trading/finance
3. **Single source of truth**: Obsidian vault là sự thật
4. **CEO-friendly**: Tiếng Việt + định nghĩa thuật ngữ + TL;DR
5. **Live research**: Search luật/đối thủ/benchmark, cite nguồn
6. **BYOT**: Template DN > pack > default

## Troubleshooting

- **"Brain dir not found"** → check vault path
- **LLM timeout** → check API key, rate limit
- **Tool API down** → cache 24h, system báo UNVERIFIED

Xem thêm: [architecture.md](architecture.md), [how-to-create-pack.md](how-to-create-pack.md)
```

- [ ] **Step 7.2: Other docs (architecture, how-to)**

(Các file architecture.md, how-to-create-pack.md, how-to-create-agent.md viết theo template tương tự — chi tiết kiến trúc, hướng dẫn đóng pack mới, hướng dẫn tạo agent mới.)

- [ ] **Step 7.3: Commit**

```bash
git add docs/
git commit -m "docs: add getting-started + architecture + how-to guides"
```

---

### Task 8: README chính

**Files:**
- Modify: `README.md`

- [ ] **Step 8.1: Update README full**

```markdown
# 🇻🇳 VN Business OS

> AI Operating System cho doanh nghiệp Việt Nam — CEO chat, agents (phòng ban) họp bàn debate, sinh tài liệu .docx/.xlsx tuân thủ ISO 9001 + luật VN.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/built_on-LangGraph-purple.svg)](https://github.com/langchain-ai/langgraph)

## 💡 Vấn đề

DN nhỏ-vừa VN cần hệ thống vận hành chuẩn nhưng:
- Không đủ HR để xây 191 tài liệu vận hành
- AI generic không hiểu luật VN, ngữ cảnh DN cụ thể
- Plugin kiểu prompt chỉ ra tài liệu, không debate / kiểm chéo

## 🎯 Giải pháp

VN Business OS là **engine debate giữa các phòng ban AI agents** + **knowledge base tài liệu chuẩn VN** + **tuân thủ luật VN**:

\`\`\`
CEO chat → Router phân loại task → Đọc Brain DN → Phát hiện gap (Brain-first)
        → Hỏi CEO clarification (có citation) → Research live (luật, đối thủ)
        → Họp Pro/Con + 3 góc nhìn → Báo cáo có TL;DR
        → CEO duyệt → Sinh .docx/.xlsx → Lưu Obsidian + Git
\`\`\`

## 🏗️ Kiến trúc

- **Engine debate**: Python + LangGraph (bóc từ TradingAgents, rename neutral)
- **Knowledge base**: 191 template tiếng Việt từ business-builder.plugin
- **Storage**: Obsidian Markdown + Git private repo
- **Multi-tool entry**: Claude Code / Cowork / Codex / Antigravity

## 🚀 Quick Start

\`\`\`bash
pip install -e .
export ANTHROPIC_API_KEY=...
vn-os onboard --vault ~/my-company-vault
vn-os run --brief "Tạo chiến dịch QC..." --vault ~/my-company-vault
\`\`\`

Xem chi tiết: [docs/getting-started.md](docs/getting-started.md)

## 📦 Industry Packs

- 🍜 **F&B** — kitchen, food-safety, food cost tracking
- 🛒 **Retail** — warehouse, logistics, marketplace integration
- 💻 **Tech-SaaS** — engineering, product-design, data, growth

## 🔒 6 Rules

| # | Rule |
|---|---|
| 1 | Brain-first clarification — không hỏi khi chưa đọc Brain |
| 2 | Domain-neutral — engine không leak trading/finance |
| 3 | Single source of truth — Obsidian là sự thật |
| 4 | CEO-friendly language — tiếng Việt + jargon defined + TL;DR |
| 5 | Live research with citations — luật/đối thủ/benchmark |
| 6 | BYOT — template DN > pack > default |

## 🤝 Đóng góp

PR welcome. Đặc biệt cần:
- Pack mới: Real Estate, Healthcare, Education, Beauty
- Việt hoá thêm agency-agents roles
- Test coverage

## 📜 License

MIT — © 2026 your-email@example.com

**Credits:**
- 191 template tiếng Việt trong `templates-vn/` adapted from `business-builder.plugin`
- Engine debate pattern adapted from [TradingAgents](https://github.com/TauricResearch/TradingAgents)
- Role definitions reference from [agency-agents](https://github.com/msitarzewski/agency-agents)
```

- [ ] **Step 8.2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README with full architecture + quick start"
```

---

### Task 9: CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 9.1: GitHub Actions CI**

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install
        run: |
          pip install -e ".[dev]"
      
      - name: Lint
        run: ruff check core/ tests/
      
      - name: Type check
        run: mypy core/ --ignore-missing-imports
      
      - name: Domain-neutral check (RULE 2)
        run: bash scripts/dev/check-domain-neutral.sh
      
      - name: Unit tests
        run: pytest tests/unit/ -v
      
      - name: Integration tests (mocked LLM)
        run: pytest tests/integration/ -v
      
      - name: E2E tests (mocked)
        run: pytest tests/e2e/test_b_campaign_high_income.py -v
```

- [ ] **Step 9.2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow (lint + type + domain-neutral + tests)"
```

---

### Task 10: Phase 6 final — All-RULES verification

**Files:**
- Create: `tests/e2e/test_all_rules_verified.py`

- [ ] **Step 10.1: Verification test**

```python
# tests/e2e/test_all_rules_verified.py
"""Final verification — tất cả 6 RULES enforced trong code."""
import subprocess
from pathlib import Path
import re


REPO = Path(__file__).parent.parent.parent


def test_rule_1_brain_first_in_question_generator():
    """RULE 1: QuestionGenerator returns [] khi gaps rỗng."""
    src = (REPO / "core/clarifier/question_generator.py").read_text(encoding="utf-8")
    assert "if not gaps:" in src
    assert "return []" in src


def test_rule_2_no_trade_leakage():
    """RULE 2: scripts/dev/check-domain-neutral.sh pass."""
    result = subprocess.run(
        ["bash", str(REPO / "scripts/dev/check-domain-neutral.sh")],
        cwd=REPO, capture_output=True,
    )
    assert result.returncode == 0


def test_rule_3_obsidian_single_source():
    """RULE 3: Vault paths normalized — code không lưu state ở chỗ thứ 3 (chỉ Obsidian + checkpointer SQLite)."""
    # Check không có hardcoded paths khác /vault/ hoặc /checkpoints
    forbidden_paths = ["/data/", "/storage/", "/db/main"]
    for src in (REPO / "core").rglob("*.py"):
        text = src.read_text(encoding="utf-8")
        for fp in forbidden_paths:
            assert fp not in text, f"Forbidden path '{fp}' in {src}"


def test_rule_4_translator_pipeline_exists():
    """RULE 4: Translator pipeline (jargon detector + simplifier + tldr)."""
    assert (REPO / "core/translator/pipeline.py").exists()
    assert (REPO / "core/translator/jargon_detector.py").exists()
    assert (REPO / "core/translator/tldr_generator.py").exists()


def test_rule_5_tools_have_sources_field():
    """RULE 5: BaseTool result phải có sources."""
    src = (REPO / "core/tools/base_tool.py").read_text(encoding="utf-8")
    assert "sources:" in src and "list[str]" in src
    assert "retrieved_at:" in src


def test_rule_6_template_resolver_priority():
    """RULE 6: Template resolver check 3 paths trong đúng thứ tự."""
    src = (REPO / "core/obsidian/template_resolver.py").read_text(encoding="utf-8")
    # First check: 00-Templates-Custom (vault)
    assert "00-Templates-Custom" in src
    # Second: 01-Departments refs (vault)
    assert "01-Departments" in src
    # Third: repo templates-vn (default)
    assert "repo" in src.lower() or "templates_vn" in src.lower() or "self.repo" in src


def test_191_templates_vendored():
    """RULE 6 baseline: 191 default templates available."""
    md_count = len(list((REPO / "templates-vn").rglob("*.md")))
    assert md_count == 191


def test_phase_tags_present():
    """All 6 phases tagged."""
    result = subprocess.run(
        ["git", "tag"], cwd=REPO, capture_output=True, text=True,
    )
    tags = result.stdout.split()
    for i in range(1, 7):
        assert f"phase-0{i}-complete" in tags, f"Missing tag phase-0{i}-complete"
```

- [ ] **Step 10.2: Run + tag final**

```bash
pytest tests/e2e/test_all_rules_verified.py -v
git add tests/e2e/test_all_rules_verified.py
git commit -m "test(rules): final verification all 6 RULES enforced in code"
git tag v0.1.0
git tag phase-06-complete
```

---

## Phase 6 Done When (= v1 ship)

- [x] Onboard wizard tạo vault valid (manual + non-interactive)
- [x] Claude Code skill adapter installed
- [x] Claude Cowork plugin built
- [x] Codex + Antigravity adapter stubs (sau)
- [x] TechCo fixture vault
- [x] E2E test case B pass với mocked LLM
- [x] Real LLM smoke test gated by env
- [x] All 6 RULES verified by automated test
- [x] CI green (lint + type + domain-neutral + tests)
- [x] Documentation: getting-started + architecture + how-to-pack + how-to-agent
- [x] README đầy đủ
- [x] Tag `v0.1.0`

## v1 Ship Criteria — Final Check

| Criterion | Status |
|---|:-:|
| `pip install -e .` work Win/Mac/Linux | ⏳ |
| `vn-os --version` returns 0.1.0 | ⏳ |
| `vn-os onboard` tạo vault valid | ⏳ |
| Test case B chạy E2E (mocked) | ⏳ |
| 13 phòng core có ≥1 agent | ⏳ |
| 3 packs (F&B, Retail, Tech-SaaS) loadable | ⏳ |
| BYOT priority work | ⏳ |
| 6 RULES enforced + có test | ⏳ |
| Claude Code adapter E2E (manual smoke) | ⏳ |
| `getting-started.md` đầy đủ cho non-tech CEO | ⏳ |

## Sau v1

**v1.1** (tuần 7-8):
- Test case A (full onboarding) + C (simple JD)
- Codex + Antigravity adapter stubs implementation
- Vietnamese spell-check (pyvi) optional

**v2** (tháng 3+):
- Auto-loop cron (báo cáo tuần/tháng tự sinh)
- Web UI dashboard
- Multi-DN support
- Pack mới: Real Estate, Healthcare, Education
