# How to Create a New Agent

## Format

Mỗi agent là 1 file `.md` với YAML frontmatter + system prompt body.

## Path

- Core dept: `departments/<dept-code>/agents/<agent-id>.md`
- Pack dept: `packs/<pack>/departments/<dept-code>/agents/<agent-id>.md`

## Frontmatter fields

| Field | Required | Type | Description |
|---|---|---|---|
| id | Y | str | Unique agent slug (kebab-case) |
| name_vn | Y | str | Tên tiếng Việt |
| department | Y | str | Dept code (vd: 07-marketing) |
| seniority | N | str | junior/mid/senior |
| emoji | N | str | Optional |
| expertise | N | list | Skills/domains |
| required_refs | N | list | Templates phải đọc |
| required_tools | N | list | Tools agent dùng |
| deliverables | N | list | Output expected |
| temperature | N | float | LLM temp (0.0-1.0) |
| model_override | N | str | Override default model |

## Body

System prompt tiếng Việt — định nghĩa vai trò, cách làm việc, nguyên tắc.

## Example

`departments/07-marketing/agents/ads-specialist.md`:
```markdown
---
id: ads-specialist
name_vn: "Chuyên viên Quảng cáo"
department: 07-marketing
seniority: senior
expertise:
  - "FB Ads"
  - "Google Ads"
  - "TikTok Ads"
required_tools:
  - vn_law_search
  - industry_benchmark
deliverables:
  - "Media plan"
  - "Budget allocation"
  - "Creative brief"
temperature: 0.6
---

# Chuyên viên Quảng cáo

## Vai trò
Bạn là chuyên viên quảng cáo digital VN với 5+ năm kinh nghiệm. Hiểu rõ FB/Google/TikTok ecosystem VN.

## Cách làm việc
1. Đọc brief + Brain (target ICP, budget)
2. Đề xuất kênh + budget allocation
3. Cite benchmark CAC/CPL ngành
4. Check legal (luật QC) qua vn_law_search

## Nguyên tắc
- LUÔN check NS available trong Brain
- Cite benchmark VN khi đề xuất KPI
- Tiếng Việt, định nghĩa thuật ngữ (CAC, CPL, ROAS)
- KHÔNG đề xuất budget vượt còn lại trong Brain
```

## Routing rule

Trong `department.yaml`, add routing rule để tự chọn agent này:

```yaml
routing_rules:
  - keywords: ["ads", "quảng cáo", "fb ads", "google ads"]
    agent: ads-specialist
```

## Test

```python
from core.agents.registry import Registry
reg = Registry(Path("departments"))
dept = reg.get("07-marketing")
agent = dept.select_agent_for_brief("Tạo chiến dịch fb ads")
assert agent.id == "ads-specialist"
```
