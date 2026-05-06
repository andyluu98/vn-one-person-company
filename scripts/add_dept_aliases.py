"""One-time script: thêm aliases_vn vào tất cả department.yaml.

Idempotent — chỉ thêm nếu chưa có.
"""
from __future__ import annotations
from pathlib import Path

import yaml


REPO = Path(__file__).parent.parent

# Map mã phòng → list aliases tiếng Việt bổ sung (ngoài name_vn đã có)
DEPT_ALIASES: dict[str, list[str]] = {
    "01-governance": ["Phòng Pháp chế", "Quản trị", "Pháp lý", "Governance"],
    "02-strategy": ["Phòng Chiến lược", "Chiến lược", "Strategy"],
    "03-finance": ["Phòng Tài chính", "Tài chính", "Kế toán", "Finance"],
    "04-people": ["Phòng Nhân sự", "Nhân sự", "HR", "People"],
    "05-operations": ["Phòng Vận hành", "Vận hành", "Operations", "Ops"],
    "06-sales": ["Phòng Kinh doanh", "Kinh doanh", "Sales"],
    "07-marketing": ["Phòng Marketing", "Marketing", "MKT"],
    "08-customer": ["Phòng Chăm sóc Khách hàng", "Khách hàng", "CSKH", "CS"],
    "09-product-tech": [
        "Phòng Sản phẩm Công nghệ", "Sản phẩm", "Công nghệ",
        "Product", "Tech", "Engineering",
    ],
    "10-training": ["Phòng Đào tạo", "Đào tạo", "Training", "L&D"],
    "11-reporting": ["Phòng Báo cáo", "Báo cáo", "Reporting", "BI", "Analytics"],
    "12-growth": ["Phòng Tăng trưởng", "Tăng trưởng", "Growth"],
    "13-kitchen": ["Phòng Bếp", "Bếp", "Kitchen"],
    "14-food-safety": ["Phòng An toàn Thực phẩm", "VSATTP", "ATTP"],
    "13-warehouse": ["Phòng Kho vận", "Kho", "Warehouse"],
    "14-logistics": ["Phòng Logistics", "Vận chuyển"],
    "13-engineering": ["Phòng Kỹ thuật", "Engineering", "Tech"],
    "14-product-design": ["Phòng Thiết kế Sản phẩm", "Design", "UX"],
    "15-data": ["Phòng Dữ liệu", "Data Science", "Data"],
}


def _process(yaml_path: Path) -> str:
    """Returns 'updated' | 'skipped' | 'unknown-code'."""
    text = yaml_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    code = data.get("code", "")
    if "aliases_vn" in data:
        return "skipped"
    if code not in DEPT_ALIASES:
        return f"unknown-code:{code}"
    data["aliases_vn"] = DEPT_ALIASES[code]
    new_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120)
    yaml_path.write_text(new_text, encoding="utf-8")
    return "updated"


def main() -> None:
    targets: list[Path] = []
    targets += list((REPO / "departments").glob("*/department.yaml"))
    targets += list((REPO / "packs").glob("*/departments/*/department.yaml"))

    counts = {"updated": 0, "skipped": 0, "unknown": 0}
    for p in targets:
        result = _process(p)
        if result == "updated":
            counts["updated"] += 1
            print(f"  [OK] {p.relative_to(REPO)}")
        elif result == "skipped":
            counts["skipped"] += 1
        else:
            counts["unknown"] += 1
            print(f"  [WARN] {p.relative_to(REPO)} — {result}")

    print(
        f"\nTotal: {counts['updated']} updated, "
        f"{counts['skipped']} skipped, {counts['unknown']} unknown"
    )


if __name__ == "__main__":
    main()
