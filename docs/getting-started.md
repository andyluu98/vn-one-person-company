# Getting Started — VN Business OS

> AI agent OS cho doanh nghiệp Việt Nam. CEO chat, agents họp bàn, sinh tài liệu.

## 1. Cài đặt

```bash
git clone <repo-url>
cd vn-business-os
pip install -e .
export ANTHROPIC_API_KEY=sk-...
export TAVILY_API_KEY=tvly-...
```

## 2. Onboard DN của bạn

```bash
vn-os onboard --vault ~/my-company-vault
```

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

```bash
vn-os run --brief "Tạo chiến dịch QC nhắm khách doanh nghiệp" --vault ~/my-company-vault
```

Hệ thống sẽ:
1. Đọc Brain
2. Phân loại task (SIMPLE/COMPLEX/STRATEGIC)
3. Phát hiện gap, tạo `03-clarification.md` với câu hỏi
4. **DỪNG** chờ bạn trả lời

Mở file, tick checkbox, lưu, rồi:

```bash
vn-os meeting <task-folder>
```

Hệ thống chạy debate giữa các phòng → tạo `07-decision-report.md` → **DỪNG** chờ bạn duyệt.

```bash
vn-os approve <task-folder>
vn-os execute <task-folder>
```

Sinh `.docx/.xlsx` vào `03-Outputs/`.

## 5. Tích hợp Claude Code / Cowork

```bash
bash adapters/claude-code/install.sh
```

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
