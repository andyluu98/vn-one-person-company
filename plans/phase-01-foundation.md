# Phase 1 — Foundation

**Goal:** Repo skeleton + Brain layer + 13 dept stubs + vendor 191 template từ bb-plugin.

**Files created:** ~50 file (Python + YAML + Markdown)
**Estimated tasks:** 12

---

### Task 1: Init repo + pyproject

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `core/__init__.py`

- [ ] **Step 1.1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "vn-business-os"
version = "0.1.0"
description = "AI-powered Operating System for Vietnamese SMEs"
authors = [{ email = "your-email@example.com" }]
license = "MIT"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "langchain-core>=0.3.0",
    "anthropic>=0.40.0",
    "google-genai>=0.3.0",
    "openai>=1.50.0",
    "pydantic>=2.8.0",
    "pyyaml>=6.0",
    "python-docx>=1.1.0",
    "openpyxl>=3.1.0",
    "tavily-python>=0.5.0",
    "click>=8.1.0",
    "rich>=13.7.0",
    "gitpython>=3.1.40",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "ruff>=0.6", "mypy>=1.10"]

[project.scripts]
vn-os = "core.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["core"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 1.2: Create `.gitignore`**

```
__pycache__/
*.py[cod]
.venv/
.env
*.db
*.docx
*.xlsx
!templates-vn/**/*.docx
!templates-vn/**/*.xlsx
.vncoderc
checkpoints/
```

- [ ] **Step 1.3: Create `LICENSE` (MIT)**

Standard MIT text với copyright "your-email@example.com 2026". (Trong NOTICE: 191 template trong `templates-vn/` adapted from business-builder.plugin; engine debate pattern adapted from TradingAgents.)

- [ ] **Step 1.4: Create `README.md`**

```markdown
# VN Business OS

AI-powered Operating System for Vietnamese SMEs. CEO chat → AI agents (phòng ban) họp bàn debate → sinh báo cáo + tài liệu .docx/.xlsx.

## Quick Start
\`\`\`bash
pip install -e .
vn-os onboard      # wizard setup vault
vn-os run --brief "<nhiệm vụ>"
\`\`\`

See `docs/getting-started.md`.
```

- [ ] **Step 1.5: Create `core/__init__.py`**

```python
"""VN Business OS core package."""
__version__ = "0.1.0"
```

- [ ] **Step 1.6: Verify**

```bash
pip install -e .
python -c "import core; print(core.__version__)"
```
Expected: `0.1.0`

- [ ] **Step 1.7: Commit**

```bash
git init
git add pyproject.toml .gitignore LICENSE README.md core/__init__.py
git commit -m "feat: init vn-business-os repo skeleton"
```

---

### Task 2: Vault scaffold template

**Files:**
- Create: `vault-template/00-Brain/strategy.md`
- Create: `vault-template/00-Brain/products.md`
- Create: `vault-template/00-Brain/budget.md`
- Create: `vault-template/00-Brain/headcount.md`
- Create: `vault-template/00-Brain/laws.md`
- Create: `vault-template/00-Brain/decisions-log.md`
- Create: `vault-template/00-Brain/state.md`
- Create: `vault-template/00-Brain/glossary.md`
- Create: `vault-template/00-Templates-Custom/README.md`
- Create: `vault-template/02-Tasks/.gitkeep`
- Create: `vault-template/03-Outputs/.gitkeep`
- Create: `vault-template/99-Archive/.gitkeep`

- [ ] **Step 2.1: Create `vault-template/00-Brain/strategy.md`**

```markdown
---
type: brain
section: strategy
last_updated: 2026-05-06
---
# Chiến lược DN

## Tầm nhìn
[Điền: tầm nhìn 3-5 năm]

## Sứ mệnh
[Điền: sứ mệnh DN]

## Khách hàng mục tiêu (ICP)
- Phân khúc: [vd: SME 5-50 nhân viên]
- Đặc điểm: [tuổi, thu nhập, hành vi]
- Pain point: [3 vấn đề chính]

## Mục tiêu năm
- Doanh thu:
- Số khách:
- Mở rộng:

## Định vị thương hiệu
[Một câu định vị]
```

- [ ] **Step 2.2: Create `vault-template/00-Brain/products.md`**

```markdown
---
type: brain
section: products
last_updated: 2026-05-06
---
# Sản phẩm / Dịch vụ

## Danh sách SP

| Mã | Tên | Giá | Margin | Trạng thái |
|---|---|---|---|---|
| | | | | |

## Tính năng nổi bật theo SP
[Điền theo SP]

## Roadmap
- Q hiện tại: [3-5 ưu tiên]
- Quý sau:
```

- [ ] **Step 2.3: Create `vault-template/00-Brain/budget.md`**

```markdown
---
type: brain
section: budget
last_updated: 2026-05-06
---
# Ngân sách

## Tổng quan năm
- Tổng ngân sách:
- Đã chi:
- Còn lại:

## Phân bổ phòng ban (quý hiện tại)

| Phòng | Cấp | Đã chi | Còn lại |
|---|---|---|---|
| Marketing | | | |
| Sales | | | |
| Operations | | | |
```

- [ ] **Step 2.4: Create `vault-template/00-Brain/headcount.md`**

```markdown
---
type: brain
section: headcount
last_updated: 2026-05-06
---
# Nhân sự / Agents

## Phòng ban đang active
[Liệt kê phòng + agents]

## Gap chuyên môn
[Phòng nào thiếu agent gì]
```

- [ ] **Step 2.5: Create `vault-template/00-Brain/laws.md`**

```markdown
---
type: brain
section: laws
last_updated: 2026-05-06
---
# Luật & Quy định liên quan DN

## Pháp lý chung VN
- Luật Doanh nghiệp 2020 (59/2020/QH14)
- Bộ luật Lao động 2019 (45/2019/QH14)
- Luật Kế toán 2015 (88/2015/QH13)

## Đặc thù ngành
[Điền theo ngành DN]

## Địa phương hoạt động
[Tỉnh/TP]
- Sở quản lý:
- Quy định địa phương:
```

- [ ] **Step 2.6: Create `vault-template/00-Brain/decisions-log.md`**

```markdown
---
type: brain
section: decisions
last_updated: 2026-05-06
---
# Nhật ký quyết định (append-only)

> Mỗi quyết định ghi 1 entry. KHÔNG xoá/sửa entry cũ.

## Format
\`\`\`
### YYYY-MM-DD — [Slug quyết định]
- Owner: CEO / Phòng X
- Quyết định: ...
- Lý do: ...
- Tham chiếu: task `02-Tasks/.../`
\`\`\`

---
```

- [ ] **Step 2.7: Create `vault-template/00-Brain/state.md`**

```markdown
---
type: brain
section: state
last_updated: 2026-05-06
---
# Trạng thái DN hiện tại

## Giai đoạn
[pre-seed / seed / growth / mature / pivot]

## Quý hiện tại
- Doanh thu:
- KPI chính:
- Vấn đề nóng:

## Runway / sức khoẻ tài chính
- Tiền mặt:
- Burn / tháng:
- Runway: [tháng]
```

- [ ] **Step 2.8: Create `vault-template/00-Brain/glossary.md`**

```markdown
---
type: brain
section: glossary
last_updated: 2026-05-06
---
# Từ điển thuật ngữ (auto-grown)

> Hệ thống tự thêm khi gặp thuật ngữ mới. CEO có thể chỉnh tay.

## Marketing
- (sẽ được sinh tự động)

## Tài chính
- (sẽ được sinh tự động)
```

- [ ] **Step 2.9: Create `vault-template/00-Templates-Custom/README.md`**

```markdown
# Templates Custom (BYOT)

Đặt template riêng của DN vào đúng folder con (theo dept code):

\`\`\`
00-Templates-Custom/
├── 01-Nhan-su/             # JD, hợp đồng LĐ, sổ tay NV
├── 02-Tai-chinh/           # phiếu thu chi, hoá đơn
├── 03-Hanh-chinh/          # SOP, biên bản
└── ...
\`\`\`

Hệ thống sẽ ưu tiên template ở đây hơn template mặc định.
Format hỗ trợ: .md, .docx, .xlsx
```

- [ ] **Step 2.10: Touch `.gitkeep` files**

```bash
touch vault-template/02-Tasks/.gitkeep
touch vault-template/03-Outputs/.gitkeep
touch vault-template/99-Archive/.gitkeep
```

- [ ] **Step 2.11: Commit**

```bash
git add vault-template/
git commit -m "feat(vault): add Obsidian vault scaffold template with Brain layer"
```

---

### Task 3: Vendor 191 templates từ bb-plugin

**Files:**
- Create: `templates-vn/` folder structure (12 dept folders)
- Create: `scripts/dev/vendor-bb-plugin.sh`

- [ ] **Step 3.1: Write vendor script**

Create `scripts/dev/vendor-bb-plugin.sh`:

```bash
#!/usr/bin/env bash
# Extract bb-plugin và copy 191 template vào templates-vn/
set -euo pipefail

PLUGIN_PATH="${1:-business-builder.plugin}"
TARGET="templates-vn"

if [ ! -f "$PLUGIN_PATH" ]; then
  echo "❌ Không tìm thấy $PLUGIN_PATH"
  exit 1
fi

TMP=$(mktemp -d)
unzip -q "$PLUGIN_PATH" -d "$TMP"

mkdir -p "$TARGET"

# Map bb-* skills → templates-vn dept codes
declare -A MAP=(
  [bb-orchestrator]="_orchestrator"
  [bb-governance]="01-governance"
  [bb-strategy]="02-strategy"
  [bb-finance]="03-finance"
  [bb-people]="04-people"
  [bb-operations]="05-operations"
  [bb-sales]="06-sales"
  [bb-marketing]="07-marketing"
  [bb-customer]="08-customer"
  [bb-product-tech]="09-product-tech"
  [bb-training]="10-training"
  [bb-reporting]="11-reporting"
  [bb-growth]="12-growth"
)

for src in "${!MAP[@]}"; do
  dst="${MAP[$src]}"
  mkdir -p "$TARGET/$dst"
  if [ -d "$TMP/skills/$src/references" ]; then
    cp -r "$TMP/skills/$src/references/"* "$TARGET/$dst/"
    echo "✓ $src → $dst ($(ls "$TARGET/$dst" | wc -l) files)"
  fi
done

rm -rf "$TMP"
echo "✅ Vendored to $TARGET/"
```

- [ ] **Step 3.2: Run vendor script**

```bash
chmod +x scripts/dev/vendor-bb-plugin.sh
bash scripts/dev/vendor-bb-plugin.sh business-builder.plugin
```

Expected: `✅ Vendored to templates-vn/` + 13 folders với 191 file tổng.

- [ ] **Step 3.3: Verify count**

```bash
find templates-vn -name "*.md" | wc -l
```
Expected: 191

- [ ] **Step 3.4: Commit**

```bash
git add scripts/dev/vendor-bb-plugin.sh templates-vn/
git commit -m "feat(templates): vendor 191 Vietnamese templates from bb-plugin"
```

---

### Task 4: Brain schema (Pydantic)

**Files:**
- Create: `core/brain/__init__.py`
- Create: `core/brain/schema.py`
- Create: `tests/unit/test_brain_schema.py`

- [ ] **Step 4.1: Write failing test**

Create `tests/unit/test_brain_schema.py`:

```python
import pytest
from core.brain.schema import (
    Strategy, Product, Budget, Headcount, BrainContext
)

def test_strategy_minimal():
    s = Strategy(vision="VN SME OS", icp="SME 5-50 NV")
    assert s.vision == "VN SME OS"

def test_product_with_price():
    p = Product(code="PRO", name="Premium", price_vnd=20_000_000, margin_pct=70)
    assert p.price_vnd == 20_000_000

def test_brain_context_assembly():
    ctx = BrainContext(
        strategy=Strategy(vision="V", icp="I"),
        products=[Product(code="A", name="X", price_vnd=1000, margin_pct=50)],
        budget=Budget(total_year_vnd=1_000_000_000, mkt_quarter_remaining_vnd=800_000_000),
        headcount=Headcount(active_departments=["07-marketing"]),
        laws=[],
        decisions=[],
        state="growth",
        glossary={},
    )
    assert ctx.products[0].name == "X"
    assert ctx.budget.mkt_quarter_remaining_vnd == 800_000_000

def test_invalid_margin_rejected():
    with pytest.raises(ValueError):
        Product(code="A", name="X", price_vnd=1000, margin_pct=150)
```

- [ ] **Step 4.2: Run test (expect FAIL)**

```bash
pytest tests/unit/test_brain_schema.py -v
```
Expected: ImportError (module not yet created).

- [ ] **Step 4.3: Implement `core/brain/schema.py`**

```python
"""Pydantic schemas cho Brain layer (00-Brain/*.md)."""
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Strategy(BaseModel):
    vision: str
    mission: Optional[str] = None
    icp: str = Field(description="Ideal Customer Profile")
    icp_details: Optional[str] = None
    yearly_goals: dict[str, str] = Field(default_factory=dict)
    positioning: Optional[str] = None


class Product(BaseModel):
    code: str
    name: str
    price_vnd: int
    margin_pct: float = Field(ge=0, le=100)
    status: str = "active"
    features: list[str] = Field(default_factory=list)


class BudgetLine(BaseModel):
    department: str
    allocated_vnd: int
    spent_vnd: int = 0

    @property
    def remaining_vnd(self) -> int:
        return self.allocated_vnd - self.spent_vnd


class Budget(BaseModel):
    total_year_vnd: int
    spent_year_vnd: int = 0
    by_department: list[BudgetLine] = Field(default_factory=list)
    mkt_quarter_remaining_vnd: int = 0


class Headcount(BaseModel):
    active_departments: list[str] = Field(default_factory=list)
    active_agents: dict[str, list[str]] = Field(default_factory=dict)
    expertise_gaps: list[str] = Field(default_factory=list)


class LawReference(BaseModel):
    name: str
    code: Optional[str] = None
    scope: str = "general"  # general | industry | local
    note: Optional[str] = None


class DecisionEntry(BaseModel):
    date: date
    slug: str
    owner: str
    decision: str
    reason: str
    task_ref: Optional[str] = None


class BrainContext(BaseModel):
    """Assembled view of toàn bộ 00-Brain/ — passed vào mọi agent."""
    strategy: Strategy
    products: list[Product]
    budget: Budget
    headcount: Headcount
    laws: list[LawReference]
    decisions: list[DecisionEntry]
    state: str
    glossary: dict[str, str]
```

- [ ] **Step 4.4: Run tests (expect PASS)**

```bash
pytest tests/unit/test_brain_schema.py -v
```
Expected: 4 passed.

- [ ] **Step 4.5: Commit**

```bash
git add core/brain/__init__.py core/brain/schema.py tests/unit/test_brain_schema.py
git commit -m "feat(brain): add Pydantic schemas for Brain layer"
```

---

### Task 5: Brain reader (parse Obsidian markdown)

**Files:**
- Create: `core/brain/reader.py`
- Create: `core/obsidian/__init__.py`
- Create: `core/obsidian/frontmatter.py`
- Create: `tests/unit/test_brain_reader.py`
- Create: `tests/fixtures/demo-vault/00-Brain/strategy.md`
- Create: `tests/fixtures/demo-vault/00-Brain/products.md`
- (Plus 5 more brain files for fixture)

- [ ] **Step 5.1: Write fixture vault**

Create `tests/fixtures/demo-vault/00-Brain/strategy.md`:

```markdown
---
type: brain
section: strategy
---
# Chiến lược

## Tầm nhìn
TechCo trở thành SaaS quản lý SME hàng đầu VN

## Khách hàng mục tiêu (ICP)
- Phân khúc: SME 5-50 nhân viên (chủ DN, không phải cá nhân)

## Mục tiêu năm
- Doanh thu: 5 tỉ
- Số khách: 200 active

## Định vị thương hiệu
SaaS đơn giản nhất cho chủ SME VN
```

Create `tests/fixtures/demo-vault/00-Brain/products.md`:

```markdown
---
type: brain
section: products
---
# Sản phẩm

| Mã | Tên | Giá | Margin | Trạng thái |
|---|---|---|---|---|
| STR | Starter | 1000000 | 60 | active |
| GRO | Growth | 5000000 | 70 | active |
| PRE | Premium | 20000000 | 75 | active |
```

(Tương tự cho budget.md, headcount.md, laws.md, decisions-log.md, state.md, glossary.md — minimal valid content)

- [ ] **Step 5.2: Write failing tests**

Create `tests/unit/test_brain_reader.py`:

```python
from pathlib import Path
import pytest
from core.brain.reader import BrainReader

FIXTURE = Path(__file__).parent.parent / "fixtures" / "demo-vault"

def test_read_strategy_returns_vision():
    reader = BrainReader(FIXTURE)
    ctx = reader.load()
    assert "TechCo" in ctx.strategy.vision

def test_read_products_returns_three():
    reader = BrainReader(FIXTURE)
    ctx = reader.load()
    assert len(ctx.products) == 3
    assert ctx.products[2].code == "PRE"
    assert ctx.products[2].price_vnd == 20_000_000

def test_missing_brain_raises():
    with pytest.raises(FileNotFoundError):
        BrainReader(Path("/nonexistent")).load()
```

- [ ] **Step 5.3: Run tests (expect FAIL)**

```bash
pytest tests/unit/test_brain_reader.py -v
```

- [ ] **Step 5.4: Implement frontmatter parser**

Create `core/obsidian/frontmatter.py`:

```python
"""Parse YAML frontmatter trong Obsidian markdown."""
from __future__ import annotations
import re
import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_str)."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}, content
    fm_yaml, body = m.groups()
    return yaml.safe_load(fm_yaml) or {}, body
```

- [ ] **Step 5.5: Implement Brain reader**

Create `core/brain/reader.py`:

```python
"""Load 00-Brain/*.md → BrainContext."""
from __future__ import annotations
import re
from pathlib import Path
from core.obsidian.frontmatter import parse as parse_frontmatter
from core.brain.schema import (
    Strategy, Product, Budget, BudgetLine, Headcount,
    LawReference, DecisionEntry, BrainContext,
)


class BrainReader:
    def __init__(self, vault_root: Path):
        self.vault = Path(vault_root)
        self.brain_dir = self.vault / "00-Brain"

    def load(self) -> BrainContext:
        if not self.brain_dir.exists():
            raise FileNotFoundError(f"Brain dir not found: {self.brain_dir}")
        return BrainContext(
            strategy=self._read_strategy(),
            products=self._read_products(),
            budget=self._read_budget(),
            headcount=self._read_headcount(),
            laws=self._read_laws(),
            decisions=self._read_decisions(),
            state=self._read_state(),
            glossary=self._read_glossary(),
        )

    def _read_file(self, name: str) -> tuple[dict, str]:
        path = self.brain_dir / name
        if not path.exists():
            return {}, ""
        return parse_frontmatter(path.read_text(encoding="utf-8"))

    def _extract_section(self, body: str, heading: str) -> str:
        """Extract content after `## heading` until next ## or EOF."""
        pattern = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)"
        m = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def _read_strategy(self) -> Strategy:
        _, body = self._read_file("strategy.md")
        vision = self._extract_section(body, "Tầm nhìn") or "(chưa điền)"
        icp = self._extract_section(body, "Khách hàng mục tiêu (ICP)") or "(chưa điền)"
        return Strategy(vision=vision, icp=icp)

    def _read_products(self) -> list[Product]:
        _, body = self._read_file("products.md")
        # Parse markdown table
        rows = re.findall(
            r"\|\s*([A-Z]+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\w+)\s*\|",
            body,
        )
        return [
            Product(code=r[0], name=r[1].strip(), price_vnd=int(r[2]),
                    margin_pct=float(r[3]), status=r[4])
            for r in rows
        ]

    def _read_budget(self) -> Budget:
        _, body = self._read_file("budget.md")
        # Minimal parse: tìm "Tổng ngân sách: X"
        total_match = re.search(r"Tổng ngân sách:\s*([\d_,]+)", body)
        total = int(re.sub(r"[_,]", "", total_match.group(1))) if total_match else 0
        return Budget(total_year_vnd=total)

    def _read_headcount(self) -> Headcount:
        _, body = self._read_file("headcount.md")
        depts = re.findall(r"^-\s+(\d{2}-[\w-]+)", body, re.MULTILINE)
        return Headcount(active_departments=depts)

    def _read_laws(self) -> list[LawReference]:
        _, body = self._read_file("laws.md")
        rows = re.findall(r"-\s+(.+?)\s*\((\d+/\d+/\w+)\)", body)
        return [LawReference(name=r[0], code=r[1]) for r in rows]

    def _read_decisions(self) -> list[DecisionEntry]:
        # Parse minimal — populate dần khi có data
        return []

    def _read_state(self) -> str:
        _, body = self._read_file("state.md")
        m = re.search(r"\[(\w[\w\s/-]+)\]", body)
        return m.group(1) if m else "unknown"

    def _read_glossary(self) -> dict[str, str]:
        _, body = self._read_file("glossary.md")
        terms = re.findall(r"^-\s+\*\*(.+?)\*\*:\s*(.+)$", body, re.MULTILINE)
        return dict(terms)
```

- [ ] **Step 5.6: Run tests (expect PASS)**

```bash
pytest tests/unit/test_brain_reader.py -v
```
Expected: 3 passed.

- [ ] **Step 5.7: Commit**

```bash
git add core/brain/reader.py core/obsidian/__init__.py core/obsidian/frontmatter.py tests/unit/test_brain_reader.py tests/fixtures/demo-vault/
git commit -m "feat(brain): add Brain reader with markdown table + section parser"
```

---

### Task 6: Memory (decisions-log append-only)

**Files:**
- Create: `core/brain/memory.py`
- Create: `tests/unit/test_memory.py`

- [ ] **Step 6.1: Write failing test**

```python
# tests/unit/test_memory.py
from datetime import date
from pathlib import Path
import tempfile
from core.brain.memory import DecisionLog
from core.brain.schema import DecisionEntry


def test_append_creates_entry(tmp_path):
    log_path = tmp_path / "decisions-log.md"
    log_path.write_text("---\ntype: brain\n---\n# Log\n", encoding="utf-8")
    
    log = DecisionLog(log_path)
    entry = DecisionEntry(
        date=date(2026, 5, 6), slug="test-decision",
        owner="CEO", decision="Approve pilot",
        reason="Brain showed budget OK"
    )
    log.append(entry)
    
    content = log_path.read_text(encoding="utf-8")
    assert "test-decision" in content
    assert "CEO" in content


def test_search_finds_matches(tmp_path):
    log_path = tmp_path / "decisions-log.md"
    log_path.write_text(
        "---\n---\n# Log\n\n### 2026-05-06 — campaign-pilot\n- Decision: launch\n- Reason: foo\n",
        encoding="utf-8",
    )
    log = DecisionLog(log_path)
    matches = log.search("campaign")
    assert len(matches) == 1
```

- [ ] **Step 6.2: Implement**

```python
# core/brain/memory.py
"""Append-only decision log."""
from __future__ import annotations
from pathlib import Path
import re
from core.brain.schema import DecisionEntry


class DecisionLog:
    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, entry: DecisionEntry) -> None:
        block = (
            f"\n### {entry.date.isoformat()} — {entry.slug}\n"
            f"- Owner: {entry.owner}\n"
            f"- Quyết định: {entry.decision}\n"
            f"- Lý do: {entry.reason}\n"
        )
        if entry.task_ref:
            block += f"- Tham chiếu: {entry.task_ref}\n"
        with self.path.open("a", encoding="utf-8") as f:
            f.write(block)

    def search(self, query: str) -> list[str]:
        if not self.path.exists():
            return []
        content = self.path.read_text(encoding="utf-8")
        blocks = re.split(r"(?=^### )", content, flags=re.MULTILINE)
        return [b for b in blocks if query.lower() in b.lower() and b.startswith("###")]
```

- [ ] **Step 6.3: Run + commit**

```bash
pytest tests/unit/test_memory.py -v
git add core/brain/memory.py tests/unit/test_memory.py
git commit -m "feat(brain): add append-only DecisionLog"
```

---

### Task 7: 13 Department stubs (department.yaml + 1 default agent each)

**Files:**
- Create: `departments/_base/department_template.yaml`
- Create: `departments/01-governance/department.yaml`
- Create: `departments/01-governance/agents/legal-officer.md`
- ... (12 more depts)

- [ ] **Step 7.1: Write template**

```yaml
# departments/_base/department_template.yaml
code: "XX-name"
name_vn: ""
name_en: ""
tier: 1
description: |
  ...
agents: []
default_speaker: ""
routing_rules: []
refs_folder: refs/
depends_on: []
debate_role:
  default: pro
```

- [ ] **Step 7.2: Create 13 dept folders + department.yaml**

Use this script `scripts/dev/create-dept-stubs.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

declare -a DEPTS=(
  "01-governance|Quản trị & Pháp lý|1"
  "02-strategy|Chiến lược & Kế hoạch|1"
  "03-finance|Tài chính & Kế toán|2"
  "04-people|Nhân sự & Con người|2"
  "05-operations|Hành chính & Vận hành|2"
  "06-sales|Kinh doanh & Bán hàng|3"
  "07-marketing|Marketing & Thương hiệu|3"
  "08-customer|Khách hàng & Dịch vụ|3"
  "09-product-tech|Sản phẩm & Công nghệ|4"
  "10-training|Đào tạo & Phát triển|4"
  "11-reporting|Báo cáo & Đo lường|4"
  "12-growth|Tăng trưởng & Đầu tư|5"
)

for entry in "${DEPTS[@]}"; do
  IFS='|' read -r code name tier <<< "$entry"
  mkdir -p "departments/$code/agents" "departments/$code/refs"
  
  cat > "departments/$code/department.yaml" <<EOF
code: "$code"
name_vn: "$name"
tier: $tier
description: "Phòng $name."
agents: []
default_speaker: ""
refs_folder: refs/
depends_on: []
debate_role:
  default: pro
EOF
  
  # Symlink refs to templates-vn (if exists)
  if [ -d "templates-vn/$code" ]; then
    rm -rf "departments/$code/refs"
    ln -s "../../templates-vn/$code" "departments/$code/refs"
  fi
done

echo "✅ Created 12 department stubs"
```

- [ ] **Step 7.3: Run + verify**

```bash
chmod +x scripts/dev/create-dept-stubs.sh
bash scripts/dev/create-dept-stubs.sh

ls departments/ | wc -l   # expect 13 (12 + _base)
ls departments/07-marketing/refs/ | head   # symlink to templates-vn
```

- [ ] **Step 7.4: Commit**

```bash
git add departments/ scripts/dev/create-dept-stubs.sh
git commit -m "feat(departments): scaffold 12 core departments with template refs"
```

---

### Task 8: Department loader (Pydantic + YAML)

**Files:**
- Create: `core/agents/__init__.py`
- Create: `core/agents/department.py`
- Create: `tests/unit/test_department_loader.py`

- [ ] **Step 8.1: Write failing test**

```python
# tests/unit/test_department_loader.py
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
```

- [ ] **Step 8.2: Implement**

```python
# core/agents/department.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class DebateRole(BaseModel):
    default: str = "pro"
    override: dict[str, str] = Field(default_factory=dict)


class RoutingRule(BaseModel):
    keywords: list[str]
    agent: str


class Department(BaseModel):
    code: str
    name_vn: str
    name_en: Optional[str] = None
    tier: int
    description: str = ""
    agents: list[str] = Field(default_factory=list)
    default_speaker: str = ""
    routing_rules: list[RoutingRule] = Field(default_factory=list)
    refs_folder: str = "refs/"
    depends_on: list[str] = Field(default_factory=list)
    debate_role: DebateRole = Field(default_factory=DebateRole)


class DepartmentLoader:
    def __init__(self, departments_root: Path):
        self.root = Path(departments_root)

    def load(self, code: str) -> Department:
        path = self.root / code / "department.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Department not found: {code}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Department(**data)

    def load_all(self) -> list[Department]:
        out = []
        for child in sorted(self.root.iterdir()):
            if child.is_dir() and child.name.startswith(("0", "1")) and (child / "department.yaml").exists():
                out.append(self.load(child.name))
        return out
```

- [ ] **Step 8.3: Run + commit**

```bash
pytest tests/unit/test_department_loader.py -v
git add core/agents/__init__.py core/agents/department.py tests/unit/test_department_loader.py
git commit -m "feat(agents): add Department + DepartmentLoader (YAML)"
```

---

### Task 9: Vault I/O wrapper

**Files:**
- Create: `core/obsidian/vault.py`
- Create: `tests/unit/test_vault.py`

- [ ] **Step 9.1: Write failing test**

```python
# tests/unit/test_vault.py
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
```

- [ ] **Step 9.2: Implement**

```python
# core/obsidian/vault.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import yaml


class ObsidianVault:
    def __init__(self, root: Path):
        self.root = Path(root)

    def read(self, rel_path: str) -> str:
        return (self.root / rel_path).read_text(encoding="utf-8")

    def write(self, rel_path: str, content: str, frontmatter: dict | None = None) -> None:
        full = self.root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        out = ""
        if frontmatter:
            out = "---\n" + yaml.safe_dump(frontmatter, allow_unicode=True) + "---\n"
        out += content
        full.write_text(out, encoding="utf-8")

    def create_task_folder(self, slug: str) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d-%H%M")
        folder = self.root / "02-Tasks" / f"{ts}-{slug}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def list_tasks(self) -> list[Path]:
        tasks_dir = self.root / "02-Tasks"
        if not tasks_dir.exists():
            return []
        return sorted([p for p in tasks_dir.iterdir() if p.is_dir()])
```

- [ ] **Step 9.3: Run + commit**

```bash
pytest tests/unit/test_vault.py -v
git add core/obsidian/vault.py tests/unit/test_vault.py
git commit -m "feat(obsidian): add Vault I/O wrapper with task folder + frontmatter"
```

---

### Task 10: CLI skeleton (click)

**Files:**
- Create: `core/cli.py`
- Create: `tests/unit/test_cli.py`

- [ ] **Step 10.1: Implement CLI stub**

```python
# core/cli.py
"""CLI entry: vn-os <command>."""
from __future__ import annotations
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option("0.1.0")
def main():
    """VN Business OS — AI agent OS for Vietnamese SMEs."""


@main.command()
@click.option("--vault", type=click.Path(), default=".", help="Path to vault")
def status(vault):
    """In trạng thái vault hiện tại."""
    from pathlib import Path
    from core.brain.reader import BrainReader
    
    try:
        ctx = BrainReader(Path(vault)).load()
        console.print(f"[green]✓[/] Brain loaded")
        console.print(f"  ICP: {ctx.strategy.icp[:60]}")
        console.print(f"  Products: {len(ctx.products)}")
        console.print(f"  Active depts: {len(ctx.headcount.active_departments)}")
    except FileNotFoundError as e:
        console.print(f"[red]✗[/] {e}")


@main.command()
@click.option("--brief", required=True, help="Task brief (Vietnamese)")
@click.option("--vault", type=click.Path(), default=".")
def run(brief, vault):
    """Chạy task qua orchestrator."""
    console.print(f"[yellow]TODO Phase 3:[/] sẽ kết nối orchestrator")
    console.print(f"Brief: {brief}")


@main.command()
def onboard():
    """Wizard tạo vault mới."""
    console.print(f"[yellow]TODO Phase 6:[/] onboard wizard")


if __name__ == "__main__":
    main()
```

- [ ] **Step 10.2: Test CLI**

```bash
pip install -e .
vn-os --version
vn-os status --vault tests/fixtures/demo-vault
vn-os run --brief "test"
```

Expected:
- Version: 0.1.0
- Status: green checks for Brain
- Run: TODO message

- [ ] **Step 10.3: Commit**

```bash
git add core/cli.py
git commit -m "feat(cli): add vn-os CLI skeleton with status/run/onboard stubs"
```

---

### Task 11: Config + LLM provider stub

**Files:**
- Create: `core/utils/__init__.py`
- Create: `core/utils/config.py`
- Create: `core/llm/__init__.py`
- Create: `core/llm/providers.py`

- [ ] **Step 11.1: Implement config loader**

```python
# core/utils/config.py
"""Load `.vncoderc` hoặc `vncode-config.yaml`."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import os
import yaml
from pydantic import BaseModel, Field


class MeetingConfig(BaseModel):
    max_perspective_rounds: int = 1
    max_debate_rounds: int = 2
    max_perspective_debate_rounds: int = 1
    total_max: int = 5


class LLMConfig(BaseModel):
    primary: str = "claude-sonnet-4-6"
    secondary: str = "gemini-3-1-pro"
    max_retries: int = 3
    max_tokens_per_task: int = 100_000
    max_cost_usd_per_task: float = 2.0


class Config(BaseModel):
    vault_path: Optional[str] = None
    meeting: MeetingConfig = Field(default_factory=MeetingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


def load_config(path: Optional[Path] = None) -> Config:
    if path and path.exists():
        return Config(**yaml.safe_load(path.read_text(encoding="utf-8")))
    # Try ~/.vncoderc
    home_path = Path.home() / ".vncoderc"
    if home_path.exists():
        return Config(**yaml.safe_load(home_path.read_text(encoding="utf-8")))
    return Config()
```

- [ ] **Step 11.2: Implement LLM provider stub**

```python
# core/llm/providers.py
"""Multi-provider LLM abstraction (stub — full impl ở Phase 4)."""
from __future__ import annotations
from typing import Protocol


class LLMProvider(Protocol):
    name: str
    
    def complete(self, messages: list[dict], model: str | None = None) -> str:
        ...


class ClaudeProvider:
    name = "claude"
    
    def __init__(self, api_key: str | None = None, default_model: str = "claude-sonnet-4-6"):
        import os
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.default_model = default_model
    
    def complete(self, messages: list[dict], model: str | None = None) -> str:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        resp = client.messages.create(
            model=model or self.default_model,
            max_tokens=4096,
            messages=messages,
        )
        return resp.content[0].text


def get_default_provider() -> LLMProvider:
    return ClaudeProvider()
```

- [ ] **Step 11.3: Commit**

```bash
git add core/utils/__init__.py core/utils/config.py core/llm/__init__.py core/llm/providers.py
git commit -m "feat(core): add config loader + Claude LLM provider stub"
```

---

### Task 12: Phase 1 smoke test

**Files:**
- Create: `tests/integration/test_phase01_smoke.py`

- [ ] **Step 12.1: Write smoke test**

```python
# tests/integration/test_phase01_smoke.py
"""Smoke test: tất cả module Phase 1 import + chạy được."""
from pathlib import Path
import subprocess


def test_import_all():
    from core.brain.schema import BrainContext
    from core.brain.reader import BrainReader
    from core.brain.memory import DecisionLog
    from core.obsidian.vault import ObsidianVault
    from core.obsidian.frontmatter import parse
    from core.agents.department import Department, DepartmentLoader
    from core.utils.config import load_config
    from core.llm.providers import ClaudeProvider


def test_cli_status_works():
    repo = Path(__file__).parent.parent.parent
    fixture = repo / "tests" / "fixtures" / "demo-vault"
    result = subprocess.run(
        ["vn-os", "status", "--vault", str(fixture)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Brain loaded" in result.stdout


def test_dept_loader_loads_12_depts():
    from core.agents.department import DepartmentLoader
    repo = Path(__file__).parent.parent.parent
    depts = DepartmentLoader(repo / "departments").load_all()
    assert len(depts) == 12


def test_templates_vn_has_191_files():
    repo = Path(__file__).parent.parent.parent
    md_files = list((repo / "templates-vn").rglob("*.md"))
    assert len(md_files) == 191
```

- [ ] **Step 12.2: Run smoke test**

```bash
pytest tests/integration/test_phase01_smoke.py -v
```
Expected: 4 passed.

- [ ] **Step 12.3: Tag Phase 1 complete**

```bash
git add tests/integration/test_phase01_smoke.py
git commit -m "test(phase-01): add smoke tests for foundation layer"
git tag phase-01-complete
```

---

## Phase 1 Done When

- [x] `pip install -e .` work
- [x] `vn-os --version` returns 0.1.0
- [x] `vn-os status` chạy ok với fixture vault
- [x] 191 template vendored vào `templates-vn/`
- [x] 12 department stubs created
- [x] Brain reader parse được 7 file Brain
- [x] DecisionLog append-only work
- [x] Vault I/O work (read/write/create_task_folder)
- [x] DepartmentLoader load được 12 dept
- [x] Phase 1 smoke test pass
