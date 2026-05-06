# How to Create an Industry Pack

Tạo pack cho ngành mới (Real Estate, Healthcare, Beauty, etc.)

## 1. Cấu trúc folder

```
packs/<pack-code>/
├── pack.yaml            # metadata
├── README.md
├── departments/
│   └── XX-new-dept/
│       ├── department.yaml
│       └── agents/
│           └── <agent-id>.md
└── brain-template/      # optional
    └── strategy.md      # override default
```

## 2. pack.yaml schema

```yaml
name: "Pack Name"
code: pack-code
version: 0.1.0
description: "Mô tả pack — ngành nào, dùng khi nào"
target_industries: ["industry1", "industry2"]
adds_departments:
  - 13-new-dept-1
  - 14-new-dept-2
extends_departments:
  - target: 05-operations    # core dept code
    add_agents:
      - new-agent-id
brain_template: brain-template/    # optional
compliance_refs:
  - "Luật ABC YYYY"
```

## 3. Department definition

`packs/<pack>/departments/13-XX/department.yaml`:
```yaml
code: "13-XX"
name_vn: "Tên phòng"
tier: 3                    # 1-5, lower = higher priority
agents:
  - agent-id-1
default_speaker: agent-id-1
refs_folder: refs/
depends_on: ["05-operations"]
debate_role:
  default: pro              # or con
```

## 4. Agent definition

`packs/<pack>/departments/13-XX/agents/agent-id.md`:
```markdown
---
id: agent-id
name_vn: "Tên Agent"
department: 13-XX
seniority: senior
expertise: ["skill1", "skill2"]
required_tools: [vn_law_search]
deliverables: ["Output 1", "Output 2"]
temperature: 0.5
---

# Tên Agent

## Vai trò
Bạn là [agent role] với [years] năm kinh nghiệm tại DN VN.

## Cách làm việc
1. Đọc brief + Brain
2. Phát biểu góc nhìn vai trò
3. Đề xuất với số liệu
4. Cite Brain mỗi nhận định

## Nguyên tắc
- LUÔN tiếng Việt
- Định nghĩa thuật ngữ
- Cite Brain
```

## 5. Test pack

```python
from core.agents.pack_loader import PackLoader
loader = PackLoader(Path("packs"))
pack = loader.load("your-pack-code")
print(pack.adds_departments)
```

## 6. Submit PR

Include:
- pack.yaml
- All dept folders + agents
- README.md
- Sample brain-template (nếu có override)
- Test verifying pack loads
