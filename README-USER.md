# VN One Person Company — Hướng dẫn cho người không biết code

> Bạn là chủ doanh nghiệp 1 người (freelancer / chủ quán / shop online / startup solo).
> Bạn muốn có **13 phòng ban AI** (Pháp lý, Tài chính, Marketing, Vận hành, Nhân sự, ...) họp bàn để ra quyết định và soạn tài liệu giúp bạn.
> Bạn **không cần biết code**. Hướng dẫn này từng bước, copy-paste, ai cũng làm được.

---

## ✨ Bạn sẽ làm được gì sau khi setup?

Sau khi cài đặt xong (~45 phút), bạn có thể chat với Claude và ra lệnh kiểu:

| Bạn nói | Hệ thống làm gì |
|---|---|
| "Soạn hợp đồng lao động cho store manager 13tr/tháng" | Phòng Pháp lý + Nhân sự debate → HĐLĐ chuẩn Bộ luật Lao động 2019, có BHXH 23.5%, đầy đủ điều khoản |
| "Lập kế hoạch chiến dịch quảng cáo Tết 50 triệu" | 5 phòng họp 3 vòng → kế hoạch + content calendar + phân bổ ngân sách |
| "Phân tích nên mở chi nhánh 2 ở quận nào" | Phòng Tài chính + Vận hành + Tăng trưởng debate → báo cáo có CAPEX, payback period, rủi ro |
| "Soạn nội quy nhân viên cho quán cafe" | Phòng Nhân sự + Pháp lý → nội quy có lương, ca làm, kỷ luật, đồng phục, thưởng |

→ **Bạn không cần thuê CFO, CMO, COO, luật sư riêng. Hệ thống là họ.**

---

## 📋 Cần chuẩn bị gì trước khi cài đặt

### Phần cứng + thời gian
- [ ] Máy tính chạy Windows 10 hoặc 11 (Mac/Linux cũng được nhưng hướng dẫn này tập trung Windows)
- [ ] Khoảng **45 phút** rảnh để cài đặt
- [ ] Internet ổn định

### Tài khoản (đăng ký miễn phí)
- [ ] Tài khoản **Anthropic Claude Pro** (~480k VNĐ/tháng — bạn có thể đã có nếu đang dùng Claude Cowork)
- [ ] Tài khoản **DeepSeek** (free, có $5 credit khi đăng ký mới — đủ chạy hàng trăm task)
- [ ] *Tùy chọn*: tài khoản **Tavily** (free tier 1000 lượt search/tháng — cần nếu muốn AI tự tra cứu luật/đối thủ trên web)

### Phần mềm sẽ cài (trong hướng dẫn)
- Python 3.11+
- Node.js 18+
- Obsidian (ghi chú + lưu trữ)
- Claude Desktop (chat với AI)

> 💡 **Đừng lo nếu chưa biết các phần mềm này là gì.** Mỗi bước hướng dẫn có link tải + thao tác cụ thể.

---

## 🚀 PHẦN 1 — CÀI ĐẶT (1 lần duy nhất, ~45 phút)

> ⚠️ **Trước khi bắt đầu:** đảm bảo bạn có quyền admin trên máy (cài phần mềm). Nếu máy công ty bị chặn — liên hệ IT.

---

### Bước 1: Cài Python (10 phút)

Python là ngôn ngữ chạy "động cơ" của hệ thống. Bạn không cần lập trình Python, chỉ cần cài để chương trình chạy được.

**Thao tác:**

1. Mở trình duyệt → vào https://www.python.org/downloads/
2. Click nút **"Download Python 3.12.x"** (hoặc bản 3.11 trở lên — không cài Python 3.10 hoặc thấp hơn)
3. Mở file vừa tải (vd `python-3.12.x-amd64.exe`)
4. **CỰC KỲ QUAN TRỌNG:** Tích vào ô **"Add python.exe to PATH"** ở dưới cùng cửa sổ install
5. Click **"Install Now"**
6. Đợi 2-3 phút đến khi thấy "Setup was successful"
7. Click **Close**

**Kiểm tra đã cài thành công:**

1. Nhấn phím **`Windows + R`** → gõ `powershell` → Enter
2. Trong cửa sổ PowerShell màu xanh đen, gõ:
   ```
   python --version
   ```
3. Nhấn Enter. Phải hiện ra: `Python 3.12.x` (hoặc 3.11.x)

❌ Nếu hiện "command not found" → Python chưa vào PATH. Cài lại bước 4 đảm bảo tích ô "Add to PATH".

---

### Bước 2: Cài Node.js (5 phút)

Node.js dùng để chạy MCP (cách Claude kết nối với các công cụ khác).

**Thao tác:**

1. Vào https://nodejs.org
2. Click nút **"LTS"** (Long Term Support — phiên bản ổn định)
3. Mở file vừa tải (vd `node-v20.x.x-x64.msi`)
4. Click **Next** → **Next** → ... → **Install** (chấp nhận mọi mặc định)
5. Đợi cài xong → **Finish**

**Kiểm tra:**

Trong PowerShell (mở mới):
```
node --version
```
Phải hiện: `v20.x.x` hoặc cao hơn.

---

### Bước 3: Cài Obsidian + plugin Local REST API (8 phút)

Obsidian là phần mềm ghi chú. Hệ thống dùng Obsidian làm "bộ nhớ" lưu mọi quyết định + tài liệu của doanh nghiệp.

**3.1 — Tải và cài Obsidian:**

1. Vào https://obsidian.md → click **"Download"**
2. Chọn **Windows installer** (hoặc 64-bit ZIP)
3. Mở file → cài đặt mặc định → Open Obsidian

**3.2 — Tạo vault (kho ghi chú) cho doanh nghiệp:**

1. Khi mở Obsidian lần đầu, click **"Create new vault"**
2. **Vault name:** đặt tên doanh nghiệp của bạn, vd: `Sao Việt`, `My Cafe`, `Acme Co`
3. **Location:** chọn ổ đĩa lớn, vd `F:\vaults` (tự tạo folder này nếu chưa có)
4. Click **Create**

→ Obsidian sẽ mở vault rỗng. Đường dẫn vault sẽ là `F:\vaults\<tên>` (vd `F:\vaults\Sao Việt`)

**3.3 — Bật chế độ cài community plugin:**

1. Click icon ⚙️ Settings (góc trái dưới Obsidian)
2. Bên trái: chọn **"Community plugins"**
3. Click **"Turn on community plugins"** → click **"Turn on"** xác nhận

**3.4 — Cài plugin "Local REST API":**

1. Vẫn ở tab Community plugins → click **"Browse"**
2. Trong ô search, gõ: `Local REST API`
3. Click vào plugin **"Local REST API"** (tác giả: coddingtonbear)
4. Click **"Install"**
5. Sau khi install xong → click **"Enable"**
6. Click **"Options"** (gear icon bên phải plugin)

**3.5 — Lấy API key của plugin:**

1. Trong settings của plugin Local REST API, tìm dòng **"API Key"**
2. Bạn sẽ thấy 1 chuỗi dài tự sinh, vd `0e957bd6...`
3. **Copy chuỗi này** → dán vào Notepad → save tạm vào file `F:\setup-keys.txt` (sau này xóa)
4. Đảm bảo plugin đang **Enabled** (toggle xanh)

> ⚠️ **Cảnh báo bảo mật:** API key này cho phép đọc/ghi/xóa toàn bộ vault. **Không chia sẻ key này cho ai.** Đừng paste vào chat AI hoặc forum công khai.

---

### Bước 4: Tải repo VN One Person Company (5 phút)

Đây là "động cơ" của hệ thống — chứa code 13 phòng ban + 192 template.

**Thao tác:**

1. Vào https://github.com/<owner>/vn-one-person-company *(thay link thật khi public)*
2. Click nút xanh **"Code"** → **"Download ZIP"**
3. Giải nén file ZIP vào ổ đĩa lớn, vd `F:\.work\vn-one-person-company`
4. Đường dẫn cuối cùng phải có dạng `F:\.work\vn-one-person-company\README.md` *(file README tồn tại trực tiếp trong folder, không nằm trong subfolder)*

> 💡 *Tip:* nếu bạn biết Git, có thể `git clone` thay vì tải ZIP — sau này update repo dễ hơn. Nhưng không bắt buộc.

---

### Bước 5: Cài thư viện Python cho repo (5 phút)

**Thao tác:**

1. Mở PowerShell (Windows + R → `powershell` → Enter)
2. Vào folder repo:
   ```powershell
   cd "F:\.work\vn-one-person-company"
   ```
3. Tạo môi trường Python ảo:
   ```powershell
   python -m venv .venv
   ```
   (Đợi 30 giây)
4. Kích hoạt môi trường:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   - Nếu có lỗi "execution policy", chạy 1 lần:
     ```powershell
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
     ```
     (Trả lời `Y` khi hỏi). Sau đó chạy lại lệnh activate.
   - Khi thành công, dòng prompt sẽ có `(.venv)` ở đầu.
5. Cài thư viện:
   ```powershell
   pip install -e .
   ```
   (Đợi 3-5 phút — sẽ thấy nhiều dòng cài đặt)
6. Kiểm tra:
   ```powershell
   vn-os --version
   ```
   Phải hiện: `vn-os, version 0.1.0` (hoặc cao hơn).

---

### Bước 6: Đăng ký DeepSeek + lấy API key (5 phút)

DeepSeek là dịch vụ AI giúp các phòng ban "suy nghĩ". Rẻ hơn Claude API ~10 lần, đủ free credit chạy hàng trăm task.

**Thao tác:**

1. Vào https://platform.deepseek.com → click **"Sign up"**
2. Đăng ký bằng email hoặc Google
3. Sau khi login → vào **"API Keys"** (menu bên trái)
4. Click **"Create new API key"** → đặt tên vd `vn-business-os`
5. **COPY KEY NGAY** (chỉ hiện 1 lần) → dán vào `F:\setup-keys.txt` cùng với key Obsidian
6. Key có dạng `sk-xxxxxxxxxxxxxxxxxxxx`

> ⚠️ **Bảo mật:** Key này cho phép gọi DeepSeek tốn tiền. **Không chia sẻ.** Nếu lỡ lộ → quay lại trang API Keys → Delete key cũ → tạo key mới.

> 💡 **Tùy chọn — đăng ký Tavily** (cho AI tự tra cứu web/luật):
> Vào https://app.tavily.com → đăng ký free → vào Settings → API Keys → tạo key. Có dạng `tvly-xxxxx`.

---

### Bước 7: Tạo file config (5 phút)

Đây là 2 file nhỏ để hệ thống biết DN của bạn ở đâu + dùng AI nào.

**7.1 — File `.env` trong vault:**

Trong PowerShell, gõ (đổi `Sao Việt` thành tên vault của bạn):

```powershell
notepad "F:\vaults\Sao Việt\.env"
```

Notepad sẽ mở file rỗng. Paste nội dung sau:

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=
```

→ Thay `sk-xxxxxxxxxxxxxxxxxxxxx` bằng key DeepSeek thật của bạn (lấy từ `F:\setup-keys.txt`).

→ Nếu có Tavily key, dán sau dấu `=` thứ 2. Nếu không → để trống.

→ **Save** (Ctrl+S) → **Close**

**7.2 — File `.vncoderc` trong home folder:**

Trong PowerShell, paste cả block sau (toàn bộ, từ `@"` đến `"@`):

```powershell
@"
llm:
  primary: deepseek-v4-pro
  secondary: deepseek-v4-flash
  max_retries: 3
  max_tokens_per_task: 100000

meeting:
  max_debate_rounds: 1
  total_max: 3

translator_mode: final_only
"@ | Out-File -FilePath "$HOME\.vncoderc" -Encoding utf8
```

Nhấn Enter. Không có output gì — vậy là xong.

---

### Bước 8: Cài Claude Desktop + 2 MCP servers (5 phút)

Claude Desktop là app chat với AI — nơi bạn ra lệnh "soạn HD lao động", "phân tích chi nhánh"...

**8.1 — Cài Claude Desktop:**

1. Vào https://claude.ai/download → tải Claude Desktop cho Windows
2. Cài đặt → Login bằng tài khoản Claude Pro của bạn

**8.2 — Cài MCP Obsidian (kết nối Claude với vault Obsidian):**

Mở PowerShell, paste:

```powershell
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Tạo file config nếu chưa có
if (!(Test-Path $configPath)) {
    New-Item -Path $configPath -ItemType File -Force | Out-Null
    '{"mcpServers": {}}' | Out-File -FilePath $configPath -Encoding utf8
}

# Mở file config trong Notepad
notepad $configPath
```

Notepad sẽ mở file `claude_desktop_config.json`. **Thay toàn bộ nội dung** bằng:

```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "PASTE_OBSIDIAN_KEY_VAO_DAY",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    },
    "vn-business-os": {
      "command": "F:\\.work\\vn-one-person-company\\.venv\\Scripts\\vn-os-mcp.exe",
      "args": []
    }
  }
}
```

→ Thay `PASTE_OBSIDIAN_KEY_VAO_DAY` bằng API key Obsidian Local REST API (từ Bước 3.5)

→ Save (Ctrl+S) → Close

**8.3 — Restart Claude Desktop:**

1. Đóng hoàn toàn Claude Desktop (right-click icon ở taskbar → Quit)
2. Mở lại Claude Desktop
3. **Quan trọng:** Obsidian app cũng phải đang chạy (vault Sao Việt đang mở). Nếu chưa → mở Obsidian.

---

### Bước 9: Verify mọi thứ chạy được (3 phút)

**9.1 — Test MCP Obsidian:**

Trong Claude Desktop chat (cửa sổ mới), gõ:

```
Liệt kê các file trong vault Obsidian của tôi
```

→ Claude phải gọi tool `obsidian_list_files_in_vault` và trả về danh sách. Nếu được → **Obsidian MCP OK**.

❌ Nếu lỗi `connection refused` → Obsidian không mở hoặc plugin Local REST API tắt. Kiểm tra lại Bước 3.

**9.2 — Test MCP vn-business-os:**

Trong Claude Desktop chat, gõ:

```
Chạy vn_status với vault F:\vaults\Sao Việt
```

→ Claude gọi tool `vn_status`. Lần đầu sẽ báo lỗi `Brain dir not found` — bình thường, vì vault chưa khởi tạo. Nhưng nghĩa là MCP đã kết nối.

❌ Nếu lỗi `Method not found` → MCP vn-business-os chưa load. Restart Claude Desktop.

---

### ✅ Cài đặt xong!

Tới đây bạn đã có:

| Thành phần | Trạng thái |
|---|---|
| Python 3.12 + Node.js 20 | ✅ |
| Obsidian + plugin Local REST API | ✅ |
| Repo vn-business-os + thư viện Python | ✅ |
| DeepSeek API key trong `.env` | ✅ |
| Config `.vncoderc` cho model | ✅ |
| Claude Desktop + 2 MCP servers | ✅ |

**Bước tiếp theo:** Phần 2 — Khởi tạo doanh nghiệp (tạo Brain + áp pack ngành).

---

## 🏢 PHẦN 2 — KHỞI TẠO DOANH NGHIỆP (1 lần duy nhất per công ty, ~30 phút)

> Bước này tạo "bộ não" của doanh nghiệp — gồm 8 file thông tin (chiến lược, sản phẩm, ngân sách, nhân sự, luật, lịch sử quyết định, tình trạng, từ điển) và cấu trúc 13 phòng ban.
>
> Sau bước này, mỗi lần bạn chat với Claude, **AI đã biết doanh nghiệp bạn là ai, đang ở giai đoạn nào** — không phải nhập lại context mỗi lần.

---

### Bước 10: Tạo cấu trúc vault Obsidian (5 phút)

Vault Obsidian cần 5 folder chính:

```
F:\vaults\<Tên DN>\
├── 00-Brain/              ← 8 file thông tin DN (AI đọc trước mỗi task)
├── 00-Templates-Custom/   ← Template riêng của bạn (tùy chọn)
├── 01-Departments/        ← 13 phòng ban core + pack ngành
├── 02-Tasks/              ← Lịch sử mọi task CEO giao
├── 03-Outputs/            ← File .docx/.xlsx được sinh ra
└── 99-Archive/            ← Task cũ đã archive
```

**Cách 1 — Tự động (khuyến nghị):**

Trong **Claude Desktop chat** (sau khi đã setup MCP ở Bước 8), gõ:

```
Khởi tạo cấu trúc vault VN Business OS tại F:\vaults\<TênDN>.
Áp pack ngành: F&B (hoặc Retail / Tech-SaaS — chọn 1).
```

→ Claude sẽ gọi tool `vn_onboard` tự động tạo các folder + copy template.

**Cách 2 — Thủ công (nếu Cách 1 lỗi):**

1. Mở **PowerShell** (Win+R → `powershell`)
2. Paste (đổi `Sao Việt` thành tên vault của bạn):

```powershell
$vault = "F:\vaults\Sao Việt"
$repo = "F:\.work\vn-one-person-company"

# Tạo 5 folder chính
New-Item -ItemType Directory -Force -Path "$vault\00-Brain" | Out-Null
New-Item -ItemType Directory -Force -Path "$vault\00-Templates-Custom" | Out-Null
New-Item -ItemType Directory -Force -Path "$vault\01-Departments" | Out-Null
New-Item -ItemType Directory -Force -Path "$vault\02-Tasks" | Out-Null
New-Item -ItemType Directory -Force -Path "$vault\03-Outputs" | Out-Null
New-Item -ItemType Directory -Force -Path "$vault\99-Archive" | Out-Null

# Copy 8 file Brain template
Copy-Item "$repo\vault-template\00-Brain\*.md" -Destination "$vault\00-Brain\" -Force

# Copy 13 phòng ban core
Copy-Item "$repo\departments\*" -Destination "$vault\01-Departments\" -Recurse -Force

Write-Host "✓ Cấu trúc vault đã tạo xong tại $vault"
```

**Verify:**

Mở Obsidian, refresh (F5). Bạn sẽ thấy 5 folder bên trái + 8 file `.md` trong `00-Brain/`.

---

### Bước 11: Áp pack ngành (5 phút)

Pack ngành thêm các phòng ban đặc thù cho doanh nghiệp của bạn:

| Pack | Phòng ban thêm | Phù hợp với |
|---|---|---|
| **F&B** | 13-kitchen, 14-food-safety | Quán ăn / cafe / nhà hàng / quán bar |
| **Retail** | 13-warehouse, 14-logistics | Shop / e-commerce / D2C / dropshipping |
| **Tech-SaaS** | 13-engineering, 14-product-design, 15-data | Startup phần mềm / app / platform |
| *(không pack)* | Chỉ 13 phòng core | Freelance / agency / dịch vụ tư vấn |

**Áp pack qua PowerShell:**

```powershell
$vault = "F:\vaults\Sao Việt"
$repo = "F:\.work\vn-one-person-company"
$pack = "fnb"   # ← Đổi thành: fnb / retail / tech-saas

# Copy phòng ban đặc thù từ pack
Copy-Item "$repo\packs\$pack\departments\*" -Destination "$vault\01-Departments\" -Recurse -Force

# Áp brain template chuyên ngành (merge với template chung)
Copy-Item "$repo\packs\$pack\brain-template\*" -Destination "$vault\00-Brain\" -Force

Write-Host "✓ Đã áp pack $pack"
```

**Verify trong Obsidian:**

Folder `01-Departments/` giờ có 13-15 sub-folder (13 core + 2-3 từ pack).

---

### Bước 12: Fill 8 file Brain — Phỏng vấn với Claude (15 phút)

Đây là bước **quan trọng nhất**. Brain rỗng = AI không biết DN bạn → output lung tung. Brain đầy đủ = AI ra quyết định chuẩn xác.

**8 file cần fill (trong `00-Brain/`):**

| File | Nội dung | Bắt buộc? |
|---|---|---|
| `strategy.md` | Tầm nhìn 3-5 năm, ICP (khách hàng mục tiêu), USP, mục tiêu năm | ✅ Bắt buộc |
| `products.md` | Menu/sản phẩm + giá + margin | ✅ Bắt buộc |
| `state.md` | Giai đoạn (pre-seed/seed/growth/mature), runway, KPI hiện tại | ✅ Bắt buộc |
| `headcount.md` | Founding team + plan tuyển + phòng ban active | ✅ Bắt buộc |
| `budget.md` | Tổng ngân sách năm, CAPEX, OPEX | 🟡 Khuyên có |
| `laws.md` | Luật/quy định ngành cần tuân thủ | 🟡 Khuyên có |
| `decisions-log.md` | Nhật ký quyết định lớn (sẽ tự sinh khi dùng) | 🟢 Tự sinh |
| `glossary.md` | Từ điển thuật ngữ DN | 🟢 Tự sinh |

> 💡 **Cách làm:** Bạn tự đọc 16 câu hỏi dưới đây + tự gõ câu trả lời vào file Brain trong Obsidian. Quy trình thủ công nhưng **an toàn 100%** — không phụ thuộc AI tool.
>
> *Tại sao không nhờ Claude tự fill?* — Vì việc ghi 8 file qua AI có thể bị timeout (giới hạn kỹ thuật 60s mỗi lượt). Tự fill nhanh + chắc chắn hơn.

**Bước 12.1 — Trả lời 16 câu hỏi (chuẩn bị nội dung)**

Mở **Notepad** (hoặc bất kỳ trình soạn thảo nào), tạo file tạm `brain-answers.txt`. Trả lời lần lượt 16 câu sau (cứ ghi gọn, sau này paste vào file thật):

**🎯 LƯỢT 1 — Chiến lược (4 câu):**

1. **Tầm nhìn 3-5 năm** — Doanh nghiệp bạn muốn đạt gì trong 3-5 năm tới? *(VD: "Trở thành chuỗi 5-10 chi nhánh cafe tầm trung tại TP.HCM")*
2. **ICP — Khách hàng mục tiêu** — Khách hàng lý tưởng là ai? Bao nhiêu tuổi? Thu nhập bao nhiêu? Pain point chính? *(VD: "Nhân viên văn phòng TP.HCM, 22-40 tuổi, thu nhập 10-30tr, ngại chờ >5 phút")*
3. **USP — Điểm khác biệt** — Bạn khác đối thủ ở chỗ nào? Tối đa 2 USP. *(VD: "Grab&go nhanh + hạt cà phê Việt chất lượng cao tầm trung")*
4. **Mục tiêu doanh thu năm đầu** — VND/năm? Bao nhiêu khách/ngày? AOV (giá trị trung bình 1 đơn) bao nhiêu? *(VD: "1.5-3 tỷ/năm, 80-150 ly/ngày, AOV 60-80k")*

**💰 LƯỢT 2 — Tài chính & quy mô (4 câu):**

5. **Vốn đầu tư ban đầu (CAPEX)** — Tổng vốn bạn có cho khởi nghiệp? Chi nhánh đầu cần bao nhiêu? *(VD: "1 tỷ tổng, 500-800tr cho chi nhánh đầu")*
6. **Nguồn vốn** — Tự có / vay / đồng sáng lập / nhà đầu tư? *(VD: "100% tự có")*
7. **Timeline khai trương** — Bao lâu nữa thì mở? *(VD: "1-3 tháng, đã có location")*
8. **Giai đoạn hiện tại** — Chọn 1 trong 5: `pre-seed` (chưa mở/ý tưởng), `seed` (mở rồi, đang test), `growth` (đang mở rộng), `mature` (ổn định), `pivot` (đang đổi hướng). *(VD: "pre-seed")*

**🍳 LƯỢT 3 — Sản phẩm & nhân sự (4 câu):**

9. **Menu/sản phẩm chính** — 5-10 SKU chính + giá + biên lợi nhuận ước. *(VD: "Cà phê đen 32k margin 70%, cà phê sữa 38k margin 70%, bánh mì 32k margin 50%")*
10. **Supplier chính** — Mua nguyên liệu/sản phẩm ở đâu? *(VD: "Hạt từ Cau Đất / Buôn Mê / Sơn La. Bánh từ supplier địa phương")*
11. **Nhân sự chi nhánh/team đầu** — Bao nhiêu người? Vai trò gì? Lương bao nhiêu? *(VD: "5-7 người: 1 quản lý 12-15tr, 1 lead barista 9-11tr, 1-2 barista 7-9tr, 2-3 phục vụ 6-8tr")*
12. **Founding team hiện tại** — Bạn solo hay có co-founder? *(VD: "Solo founder, chưa có co-founder")*

**📊 LƯỢT 4 — KPI & vận hành (4 câu):**

13. **KPI ưu tiên track hàng tuần** — Số ly/ngày? AOV? Food cost%? Customer return rate? Revenue/m²? *(VD: "Số ly/ngày + AOV")*
14. **Kế hoạch nhượng quyền (franchise)** — Có / Không / Sau Y3 / Chưa quyết. *(VD: "Có, sau khi prove model 2-3 chi nhánh self-owned")*
15. **Compliance — luật cần tuân thủ** — Liệt kê các quy định ngành. *(VD: "VSATTP NĐ 15/2018, PCCC TCVN 5738:2021, Bộ luật Lao động 2019, Luật BVNTD 2023")*
16. **Brand identity** — Tên thương hiệu + slogan (nếu có) + positioning. *(VD: "Tên: Sao Việt. Slogan: 'Hạt Việt đậm. Gọn trong tay.' Positioning: cafe Việt nhanh-tiện cho văn phòng")*

---

**Bước 12.2 — Mở 8 file template trong Obsidian + paste câu trả lời**

Trong Obsidian (vault Sao Việt đang mở), mở từng file trong folder `00-Brain/` và điền theo hướng dẫn dưới.

⚠️ **CỰC KỲ QUAN TRỌNG về format heading** — Hệ thống parser yêu cầu heading **CHÍNH XÁC**, không có suffix. Sai 1 chữ là parser không đọc được.

---

**📄 File 1: `strategy.md`** *(dùng câu 1, 2, 3, 4)*

Mở file → xóa toàn bộ → paste:

```markdown
---
type: brain
section: strategy
aliases: ["Chiến lược", "Strategy", "Tầm nhìn"]
last_updated: 2026-05-08
---
# Chiến lược DN — <Tên DN>

## Tầm nhìn
<Trả lời câu 1 — không thêm ngoặc kép, không thêm "(3-5 năm)" vào heading>

## Sứ mệnh
<1-2 câu mô tả lý do tồn tại của DN>

## Khách hàng mục tiêu (ICP)
- **Phân khúc:** <từ câu 2>
- **Tuổi:** <từ câu 2>
- **Thu nhập:** <từ câu 2>
- **Hành vi:** <từ câu 2>
- **Pain point:** <từ câu 2>

## Mục tiêu năm đầu
- Doanh thu: <từ câu 4>
- Số khách/ngày: <từ câu 4>
- AOV: <từ câu 4>

## Định vị thương hiệu
<1 câu positioning, từ câu 16 nếu có>

## USP
<từ câu 3, ghi 1-2 dòng bullet>
```

✅ **Heading bắt buộc đúng:** `## Tầm nhìn` và `## Khách hàng mục tiêu (ICP)` — viết y hệt.

---

**📄 File 2: `state.md`** *(dùng câu 8)*

```markdown
---
type: brain
section: state
last_updated: 2026-05-08
---
# Trạng thái DN hiện tại

## Giai đoạn
[<từ câu 8 — chọn 1: pre-seed / seed / growth / mature / pivot>]

<1-2 đoạn mô tả thêm về tình trạng hiện tại>

## Quý hiện tại
- Doanh thu: <số nếu có, hoặc "0 (chưa mở)">
- KPI chính: <từ câu 13>
- Vấn đề nóng: <liệt kê 2-3 vấn đề lớn nhất>

## Runway / sức khoẻ tài chính
- Tiền mặt: <từ câu 5>
- Burn/tháng: <ước>
- Runway: <số tháng>
```

✅ **Bắt buộc:** dòng `[pre-seed]` (hoặc giai đoạn khác trong dấu ngoặc vuông) — parser tìm chuỗi này.

---

**📄 File 3: `products.md`** *(dùng câu 9)*

```markdown
---
type: brain
section: products
last_updated: 2026-05-08
---
# Sản phẩm — <Tên DN>

## Menu chính

| Code | Tên | price | margin | status |
|---|---|---|---|---|
| CFD | Cà phê đen phin | 32000 | 70 | active |
| CFS | Cà phê sữa phin | 38000 | 70 | active |
| BX | Bạc xỉu | 42000 | 65 | active |
<thêm các SKU từ câu 9, mỗi dòng 1 SKU>

## Supplier
<từ câu 10>
```

✅ **Bắt buộc:** Table phải có **đúng 5 cột với header `Code | Tên | price | margin | status`**. Code viết HOA (vd `CFD`, không `cfd`). Price ghi số nguyên (32000, không 32k).

---

**📄 File 4: `headcount.md`** *(dùng câu 11, 12)*

```markdown
---
type: brain
section: headcount
last_updated: 2026-05-08
---
# Nhân sự & Phòng ban — <Tên DN>

## Founding team
- CEO: <tên + email từ câu 12>
<liệt kê co-founder nếu có>

## Phòng ban active

- 01-governance — <ai phụ trách, vd "CEO direct">
- 02-strategy — CEO direct
- 03-finance — CEO direct
- 04-people — CEO direct
- 05-operations — CEO direct
- 06-sales — <vai trò>
- 07-marketing — <vai trò>
- 08-customer — <vai trò>
- 10-training — <vai trò>
- 11-reporting — <vai trò>
- 12-growth — <vai trò>
<thêm phòng pack ngành nếu có:>
- 13-kitchen — <F&B pack>
- 14-food-safety — <F&B pack>

## Kế hoạch nhân sự chi nhánh đầu
<từ câu 11>
```

✅ **Bắt buộc:** mỗi phòng ban là 1 dòng bullet bắt đầu bằng `- <số 2 chữ số>-<tên>` (vd `- 01-governance`). Parser dùng regex tìm pattern này.

---

**📄 File 5: `budget.md`** *(dùng câu 5)*

```markdown
---
type: brain
section: budget
last_updated: 2026-05-08
---
# Ngân sách — <Tên DN>

Tổng ngân sách: <số nguyên VND, vd "1000000000" cho 1 tỷ>

## CAPEX (chi nhánh đầu)
<liệt kê các hạng mục từ câu 5>

## OPEX (vận hành tháng)
<liệt kê thuê, lương, COGS, điện nước...>

## Buffer / Runway
<tính dựa trên vốn còn lại>
```

✅ **Bắt buộc:** Dòng `Tổng ngân sách: <số>` viết y hệt (parser tìm pattern này). Số ghi nguyên, không có dấu phẩy/chấm/từ "tỷ".

---

**📄 File 6: `laws.md`** *(dùng câu 15)*

```markdown
---
type: brain
section: laws
last_updated: 2026-05-08
---
# Luật & Compliance — <Tên DN>

## Nhóm 1: Đăng ký kinh doanh
- [ ] GPKD hộ cá thể hoặc công ty TNHH
- [ ] Mã số thuế

## Nhóm 2: Compliance ngành
<từ câu 15, liệt kê>

## Nhóm 3: Lao động
- Bộ luật Lao động 2019
- BHXH/BHYT 23.5%

## Nhóm 4: Thuế
- VAT 8% (F&B, ưu đãi 2024-2026)
- TNDN 20%
```

---

**📄 File 7: `decisions-log.md`** — *(để trống lúc đầu, AI tự ghi sau khi chạy task)*

```markdown
---
type: brain
section: decisions
last_updated: 2026-05-08
---
# Nhật ký quyết định

> Append-only. Mỗi quyết định lớn được ghi ở đây.

## [2026-05-08] Khởi tạo Brain DN
**Quyết định:** Setup VN Business OS với industry pack <ngành của bạn>.
**Người ra quyết định:** CEO
```

---

**📄 File 8: `glossary.md`** — *(template tối thiểu, AI sẽ thêm thuật ngữ mới khi gặp)*

```markdown
---
type: brain
section: glossary
last_updated: 2026-05-08
---
# Từ điển thuật ngữ

## Tài chính
- **AOV**: Giá trị trung bình một đơn hàng (Average Order Value).
- **CAPEX**: Chi phí đầu tư ban đầu, mua tài sản dài hạn.
- **OPEX**: Chi phí vận hành hàng tháng.
- **COGS**: Giá vốn hàng bán.
- **Break-even**: Điểm hòa vốn.
- **Runway**: Số tháng trụ được nếu doanh thu = 0.

## Pháp lý VN
- **VSATTP**: Vệ sinh An toàn Thực phẩm. NĐ 15/2018/NĐ-CP.
- **PCCC**: Phòng cháy chữa cháy. TCVN 5738/2021.
- **GPKD**: Giấy phép kinh doanh.
- **VAT**: Thuế giá trị gia tăng.
- **TNDN**: Thuế thu nhập doanh nghiệp 20%.
- **TNCN**: Thuế thu nhập cá nhân.
- **ICP**: Hồ sơ khách hàng lý tưởng (Ideal Customer Profile).
```

✅ **Bắt buộc:** Mỗi thuật ngữ format `- **Term**: định nghĩa` (có dấu hai chấm `:` ngay sau dấu `**` đóng). Không dùng em dash `—`.

---

**Bước 12.3 — Save tất cả file**

Trong Obsidian, mỗi file sau khi paste content + thay placeholder, nhấn **Ctrl+S** để save.

Nếu Obsidian có config "Auto-save" (mặc định bật) → file tự save khi chuyển tab.

---

### Bước 13: Verify Brain đã đầy đủ (2 phút)

Trong **Claude Desktop chat**, gõ:

```
Chạy vn_status với vault F:\vaults\Sao Việt
```

**Kết quả mong đợi:**

```json
{
  "vault": "F:\\vaults\\Sao Việt",
  "icp": "- Phân khúc: Nhân viên văn phòng TP.HCM\n- Tuổi: 22-40...",   ✅ KHÔNG được là "(chưa điền)"
  "vision": "Trở thành chuỗi 5-10 chi nhánh...",                          ✅ KHÔNG được là "(chưa điền)"
  "products": 10,                                                          ✅ Phải > 0
  "active_departments": ["01-governance", "02-strategy", ...],            ✅ Phải có ≥ 13 entries
  "state": "pre-seed",                                                    ✅ KHÔNG được là "unknown"
  "tools_live": ["web_search", "vn_law_search", ...],                     ✅ 6 tools nếu có Tavily key
  "packs": []
}
```

**Nếu thấy:**

- `vision: "(chưa điền)"` → Brain chưa fill hoặc heading sai format. Quay lại Bước 12.
- `products: 0` → File `products.md` thiếu table với schema `| Code | Tên | price | margin | status |`.
- `state: "unknown"` → File `state.md` thiếu dòng `[pre-seed]` (hoặc giai đoạn khác trong ngoặc vuông).
- `active_departments: []` → File `headcount.md` thiếu bullet list phòng ban dạng `- 01-governance`.

---

### ✅ Khởi tạo xong!

Tới đây bạn có:

| Thành phần | Trạng thái |
|---|---|
| Vault với 5 folder chuẩn | ✅ |
| 13 phòng ban core + pack ngành | ✅ |
| 8 file Brain đầy đủ thông tin DN | ✅ |
| `vn_status` báo các trường đều có data | ✅ |

**Bước tiếp theo:** Phần 3 — Sử dụng hàng ngày.

---

## 💼 PHẦN 3 — SỬ DỤNG HÀNG NGÀY

> Đây là phần bạn sẽ đọc đi đọc lại nhiều nhất. Phần 1-2 chỉ làm 1 lần, **Phần 3 là cách bạn vận hành DN hàng ngày**.

---

### 📌 Quy tắc vàng — Phân loại task trước khi giao

Hệ thống có **2 môi trường** để chạy task:

1. **Claude Desktop chat** (Cowork) — bạn chat với Claude trực tiếp
2. **PowerShell** (cửa sổ đen của Windows) — chạy lệnh `vn-os` trực tiếp

Lý do **phải dùng cả 2**: Claude Desktop có giới hạn kỹ thuật **60 giây** cho mỗi tool call. Task nặng (cần AI suy nghĩ nhiều) sẽ vượt 60 giây → fail. PowerShell không có giới hạn này → task nặng phải chạy ở đó.

**Bảng phân loại — học thuộc bảng này:**

| Task của bạn | Môi trường | Lý do |
|---|---|---|
| "Tóm tắt vault, doanh nghiệp tôi đang ở giai đoạn nào?" | 🟢 **Cowork chat** | Chỉ đọc Brain, không LLM heavy |
| "Mở file 07-decision-report.md task X cho tôi xem" | 🟢 **Cowork chat** | Đọc file qua Obsidian MCP |
| "Sửa file budget.md, thêm khoản chi marketing 20tr" | 🟢 **Cowork chat** | Sửa file qua Obsidian MCP |
| "Tư vấn xem có nên tăng giá menu không?" | 🟢 **Cowork chat** | Claude tư vấn dựa trên Brain — không cần gọi tool VN OS |
| "Soạn JD barista cho tôi" | 🔴 **PowerShell** | 1+ LLM call → timeout |
| "Soạn HD lao động store manager 13tr" | 🔴 **PowerShell** | 1+ LLM call → timeout |
| "Brainstorm slogan + visual identity Sao Việt" | 🔴 **PowerShell** | Cần debate đa phòng → 7+ LLM calls |
| "Phân tích nên mở chi nhánh 2 ở quận nào" | 🔴 **PowerShell** | Quyết định chiến lược → cần meeting |
| "Lập kế hoạch chiến dịch QC Tết 50tr" | 🔴 **PowerShell** | Quyết định chiến lược → cần meeting |
| "Render decision report task X ra file .docx" | 🟡 **Thử Cowork trước** | Render template, không LLM (trừ fallback). Nếu lỗi → PS. |

**Mẹo nhớ nhanh:**
- 🟢 Nếu task của bạn **chỉ đọc/sửa file** (không cần AI sáng tạo nội dung mới) → **Cowork**
- 🔴 Nếu task **cần AI tạo nội dung mới** (soạn doc, debate, brainstorm) → **PowerShell**

---

### 🟢 Workflow A — Task NHẸ (Cowork chat)

Mở Claude Desktop → bắt đầu chat mới. Cứ chat tự nhiên như với 1 trợ lý hiểu rõ DN của bạn.

**Ví dụ 1 — Tóm tắt vault:**

> **Bạn:** Vault Sao Việt của tôi đang trạng thái như nào? Có task nào pending không?

Claude tự gọi `vn_status`, đọc, trả lời:
> Doanh nghiệp Sao Việt đang ở giai đoạn pre-seed (chưa khai trương). Bạn có 10 SKU sản phẩm, 13 phòng ban active. Các tools research (web/luật/đối thủ) đều sẵn sàng. Hiện có 14 task trong `02-Tasks/`, trong đó task `2026-05-08-1105-test-...` đã có decision report.

**Ví dụ 2 — Đọc decision report cũ:**

> **Bạn:** Mở file `02-Tasks/2026-05-08-1105-test-liet-ke-3-y-tuong-slogan/07-decision-report.md` cho tôi, tóm tắt 3 ý chính.

Claude gọi `obsidian_get_file_contents`, đọc, tóm tắt:
> Hệ thống đề xuất slogan **"Hạt Việt đậm. Gọn trong tay."** Lý do chính: (1) An toàn pháp lý (không cam kết "5 giây"), (2) dùng được cho cả 6 SKU cà phê, (3) khôn ngoan vì chưa cần cam kết loại hạt cụ thể. CEO cần chốt 4 việc trước khi in bảng hiệu...

**Ví dụ 3 — Sửa file Brain:**

> **Bạn:** Trong file 00-Brain/budget.md, đổi tổng ngân sách từ 1 tỷ thành 1.5 tỷ.

Claude dùng `obsidian_patch_content`, sửa file → confirm: "Đã update file budget.md. Tổng ngân sách giờ là 1500000000 VND."

**Ví dụ 4 — Tư vấn (không gọi tool):**

> **Bạn:** Dựa trên Brain Sao Việt, theo bạn tôi nên focus mở chi nhánh 2 hay nâng cao chất lượng chi nhánh 1 trước?

Claude đọc context từ chat trước (hoặc gọi `vn_status` để load Brain), trả lời tư vấn dựa trên data. Không cần gọi tool VN OS heavy.

---

### 🔴 Workflow B — Task NẶNG (Hybrid Cowork + PowerShell)

Đây là **pattern chính** khi bạn cần soạn doc hoặc ra quyết định lớn.

**4 bước chuẩn:**

**Bước B1 — Trong Cowork chat, ra lệnh tự nhiên:**

> **Bạn:** Tôi muốn soạn HD lao động cho store manager Sao Việt, lương 13tr/tháng, yêu cầu 1 năm KN F&B + leadership tiềm năng.

**Bước B2 — Claude trả về command PowerShell:**

Claude sẽ phân loại task → biết đây là task NẶNG → trả về command PowerShell sẵn sàng paste:

> **Claude:** Task này cần debate đa phòng (Pháp lý + Nhân sự + Tài chính). Mình KHÔNG chạy được trong chat này (timeout 60s). Bạn copy command sau vào PowerShell:
>
> ```powershell
> cd "F:\vaults\Sao Việt"
> $vnos = "F:\.work\vn-one-person-company\.venv\Scripts\vn-os.exe"
>
> # Stage 1: tạo task folder + phân loại
> & $vnos run --vault . --brief "HD lao động store manager Sao Việt, lương 13tr/tháng, 1 năm KN F&B + leadership tiềm năng, quản lý team 5-7 người chi nhánh grab&go 50-80m2."
> ```
>
> Đợi ~30 giây. Sau khi return prompt, copy command tiếp theo.
>
> Ước tính tổng thời gian: ~3-5 phút (qua đầy đủ pipeline).
> Bạn cứ đi việc khác — vào Obsidian thấy folder mới trong `02-Tasks/`. Báo mình "xong" để mình check kết quả.

**Bước B3 — User mở PowerShell, paste, đợi:**

1. Mở PowerShell (Win+R → `powershell` → Enter) — **giữ cửa sổ này mở suốt session**
2. Paste lệnh đầu tiên (`cd ...` + `$vnos = ...` + `& $vnos run ...`)
3. Đợi 30s-1p → return prompt + in ra `task_folder` (vd `02-Tasks\2026-05-08-1230-...`)
4. Quay lại Cowork chat, paste output cho Claude xem (hoặc báo "task folder: ...")
5. Claude gửi command tiếp theo (`vn-os meeting`, rồi `vn-os approve`, rồi `vn-os execute`)
6. Lặp đến khi xong

**Bước B4 — Vào Obsidian xem kết quả:**

Sau mỗi stage, file mới xuất hiện trong vault:

| Stage | File mới | Bạn cần làm gì |
|---|---|---|
| `vn-os run` | `00-brief.md`, `01-routing.md`, `02-context.md`, có thể `03-clarification.md` | Nếu có `03-clarification.md` → mở, **trả lời câu hỏi**, save |
| `vn-os resume` (nếu có clarification) | `03-clarification-answered.md` | (tự động) |
| `vn-os meeting` | `03b-research-findings.md`, `04-meeting-r1-perspectives.md`, `05-meeting-r2-debate.md`, `06-meeting-r3-perspectives.md`, `07-decision-report.md` | **Mở `07-decision-report.md` đọc + duyệt** |
| `vn-os approve` | `08-execution-plan.md` | Đọc plan, OK chưa? |
| `vn-os execute` | `03-Outputs/<task>/<file>.docx` (hoặc .xlsx) | **Mở file .docx → đó là deliverable cuối cùng** |

---

### 📋 Pipeline đầy đủ 5 stage — Khi nào cần dùng?

| Loại task | Stage cần chạy | Thời gian ước |
|---|---|---|
| **SIMPLE** (vd "soạn JD barista") | `run` → `meeting` → `approve` → `execute` | ~3-5 phút |
| **COMPLEX cần clarification** (vd "lập kế hoạch QC Tết") | `run` → trả lời clarification → `resume` → `meeting` → `approve` → `execute` | ~5-10 phút |
| **STRATEGIC** (vd "mở chi nhánh 2") | Same as COMPLEX nhưng meeting có nhiều rounds debate hơn | ~10-15 phút |

**Pattern command đầy đủ (template, copy-paste):**

```powershell
# Setup 1 lần đầu mỗi cửa sổ PS:
cd "F:\vaults\Sao Việt"
$vnos = "F:\.work\vn-one-person-company\.venv\Scripts\vn-os.exe"

# Stage 1 — Tạo task folder + phân loại + clarification (nếu cần)
& $vnos run --vault . --brief "<brief của bạn ở đây>"
# → return: task_folder = 02-Tasks\2026-MM-DD-HHMM-<slug>\
#   stage = PAUSE_CLARIFICATION (nếu cần CEO trả lời) hoặc PAUSE_DECISION_REPORT (sẵn sàng meeting)

# Nếu PAUSE_CLARIFICATION:
#   1. Mở Obsidian → 02-Tasks\<folder>\03-clarification.md
#   2. Đọc câu hỏi, viết câu trả lời ngay dưới mỗi câu, save (Ctrl+S)
#   3. Quay lại PowerShell, chạy:
& $vnos resume "02-Tasks\<task_folder>"

# Stage 3 — Meeting (debate đa phòng → decision report)
& $vnos meeting "02-Tasks\<task_folder>"
# → return: PAUSE_DECISION_REPORT, file 07-decision-report.md đã được tạo

# >>> CHECKPOINT: Mở 07-decision-report.md trong Obsidian, ĐỌC + REVIEW <<<
# Nếu OK với khuyến nghị → tiếp Stage 4
# Nếu muốn sửa → sửa thẳng file 07-decision-report.md trong Obsidian, save, rồi tiếp

# Stage 4 — Approve → execution plan
& $vnos approve "02-Tasks\<task_folder>"
# → return: file 08-execution-plan.md đã được tạo

# Stage 5 — Execute → render .docx/.xlsx
& $vnos execute "02-Tasks\<task_folder>"
# → return: DONE, file .docx/.xlsx trong vault\03-Outputs\<task>\
```

**Lưu ý quan trọng — Stop 1 + Stop 2:**

Hệ thống có **2 điểm dừng cố ý** để CEO duyệt:

- **Stop 1** — sau `meeting`: bạn xem `07-decision-report.md` trước khi approve. **Đây là cơ hội từ chối/sửa quyết định trước khi hệ thống render docx.**
- **Stop 2** — sau `approve`: bạn xem `08-execution-plan.md` trước khi execute. **Đây là cơ hội xem plan triển khai chi tiết, từ chối/sửa trước khi tốn template render.**

→ **Đừng bỏ qua 2 điểm dừng này.** Nếu hệ thống đề xuất tệ → sửa thẳng file `07-decision-report.md` hoặc `08-execution-plan.md` trong Obsidian, **rồi mới chạy stage tiếp theo**.

---

### 📖 Cách review decision report

File `07-decision-report.md` có cấu trúc chuẩn:

```markdown
# Báo cáo quyết định: <chủ đề>

## 📌 Tóm lại (đọc 30 giây)
- 3-5 dòng tóm tắt cho CEO
- Khuyến nghị chính

## Khuyến nghị
**Tiến hành / Tiến hành nhưng có điều chỉnh / Không tiến hành** — <giải thích>

## Phân tích chi tiết
### Mỗi bộ phận nói gì
<phòng Marketing nói..., phòng Tài chính nói..., ...>

### Tranh luận Ủng hộ vs Phản đối
| Phe | Luận điểm | Dẫn nguồn |

### 3 góc nhìn (Tăng trưởng / Thận trọng / Cân bằng)

## Việc cần làm ngay (Action items)
| # | Việc | Ai | Hạn | Chi phí |

## Cột mốc đo hiệu quả
| Tuần X | KPI | Ngưỡng | Hành động nếu fail |

## Câu hỏi cần CEO quyết
A. ...  B. ...  C. ...  D. ...

## ⚠️ Cảnh báo: Claims thiếu trích nguồn
<liệt kê các claim cần verify>
```

**Cách đọc nhanh (5 phút):**

1. Đọc **TL;DR** ở đầu (30 giây)
2. Đọc **Khuyến nghị** (xem hệ thống bảo "Tiến hành" hay "Không")
3. Scan **Việc cần làm ngay** (có item nào quá đắt hay quá gấp không?)
4. Đọc **Cảnh báo Claims thiếu trích nguồn** — nếu có số liệu quan trọng → tự verify
5. Trả lời **Câu hỏi CEO quyết** (A/B/C/D) → ghi vào file decision-log hoặc edit thẳng file decision-report

**Khi nào KHÔNG nên approve:**

- 🔴 Khuyến nghị "Tiến hành" nhưng claims thiếu citation cho số liệu lớn (vd: "doanh thu sẽ tăng 30%" không có nguồn)
- 🔴 Action items có chi phí vượt budget
- 🔴 Phe Phản đối có argument mạnh mà phe Ủng hộ chưa rebuttal được
- 🔴 Bạn cảm thấy "không hợp lý" — instinct của founder thường đúng

→ Edit thẳng `07-decision-report.md` (sửa khuyến nghị, thêm note), rồi chạy `approve` sau.

---

### 💡 Tip: Setup PowerShell shortcut mở sẵn vault

Để mỗi lần làm việc không phải gõ `cd` + `$vnos = ...`, tạo shortcut sẵn:

**Tạo file `vn-os-shell.ps1` trong vault:**

```powershell
# Tạo file shortcut
notepad "F:\vaults\Sao Việt\vn-os-shell.ps1"
```

Notepad mở → paste:

```powershell
# vn-os shell — auto-setup environment
Set-Location "F:\vaults\Sao Việt"
$global:vnos = "F:\.work\vn-one-person-company\.venv\Scripts\vn-os.exe"
Write-Host "✓ Vault: $(Get-Location)" -ForegroundColor Green
Write-Host "✓ vn-os: $vnos" -ForegroundColor Green
Write-Host "Sẵn sàng. Dùng: & `$vnos run --vault . --brief `"...`""
```

Save → Close.

**Tạo shortcut trên Desktop để click mở luôn:**

1. Right-click Desktop → New → Shortcut
2. Location: `powershell.exe -NoExit -File "F:\vaults\Sao Việt\vn-os-shell.ps1"`
3. Name: **"VN OS - Sao Việt"**
4. Click Finish

Từ giờ click shortcut này → PowerShell mở sẵn ở vault, biến `$vnos` đã set, sẵn sàng paste lệnh `& $vnos run ...`.

---

### ⏱️ Bảng thời gian ước tính

| Tác vụ | Thời gian thực tế |
|---|---|
| `vn_status` qua Cowork | < 1 giây |
| Đọc/sửa file qua Obsidian MCP | 1-5 giây |
| `vn-os run` (1 task SIMPLE) | 30-60 giây |
| `vn-os run` (cần clarification) | 30-60 giây + thời gian bạn trả lời |
| `vn-os meeting` (DeepSeek v4-pro thinking off) | 1-3 phút |
| `vn-os meeting` (DeepSeek thinking on) | 5-10 phút *(không khuyến nghị)* |
| `vn-os approve` | 30-60 giây |
| `vn-os execute` (render docx) | 5-15 giây |
| **Tổng pipeline 1 task SIMPLE** | **3-5 phút** |
| **Tổng pipeline 1 task COMPLEX** | **5-10 phút** |

→ **Nếu chậm hơn benchmark này nhiều** (vd meeting > 10 phút) → có thể bị treo. Ctrl+C, kiểm tra Obsidian xem có file mới được tạo không, retry.

---

### 🔄 Quy trình "Một ngày làm việc với VN OS"

Đây là pattern bạn sẽ làm mỗi ngày khi đã quen:

**Sáng (5 phút):**
1. Mở Claude Desktop chat mới
2. Hỏi: "Vault có gì mới? KPI tuần này thế nào?"
3. Claude tóm tắt → bạn biết focus hôm nay

**Khi có task lớn (3-10 phút):**
1. Trong Cowork: ra lệnh "Soạn ..." / "Phân tích ..."
2. Click shortcut "VN OS - Sao Việt" → PS mở
3. Paste command Claude gửi
4. Đợi (đi việc khác)
5. Vào Obsidian review file kết quả
6. Quay lại Cowork → "Xong, tóm tắt giúp tôi"

**Cuối tuần (10 phút):**
1. Trong Cowork: "Liệt kê các quyết định lớn tuần này từ 02-Tasks/"
2. "Update file 00-Brain/decisions-log.md với 3 quyết định quan trọng nhất"
3. Claude tự sửa file qua Obsidian MCP

---

## 🚧 Đang viết các phần tiếp theo

- 🔧 PHẦN 4 — Khắc phục lỗi thường gặp (sắp có)
- 💡 PHẦN 5 — Mẹo dùng tốt nhất (sắp có)
- 🤝 PHẦN 6 — Dành cho dev (sắp có)

---

**Có vấn đề trong Phần 1, 2 hoặc 3?** Mở issue tại: https://github.com/&lt;owner&gt;/vn-one-person-company/issues
