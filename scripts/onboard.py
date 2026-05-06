"""Onboarding wizard — tạo vault mới cho DN."""
from __future__ import annotations
import shutil
from pathlib import Path
import click
from rich.console import Console
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
        if not non_interactive:
            from rich.prompt import Confirm
            if not Confirm.ask(f"⚠️  {vault_path} đã có dữ liệu. Tiếp tục? (sẽ ghi đè)"):
                console.print("[red]Hủy.[/]")
                return
        # In non-interactive mode, proceed silently (overwrite)

    # Step 1: Copy vault scaffold
    console.print("[bold]Bước 1/5:[/] Tạo vault scaffold...")
    shutil.copytree(repo / "vault-template", vault_path, dirs_exist_ok=True)
    console.print(f"  ✓ Vault tạo tại {vault_path}")

    # Step 2: Hỏi DN ngành gì
    console.print("\n[bold]Bước 2/5:[/] Chọn industry pack")
    if non_interactive:
        selected_packs = []
    else:
        from rich.prompt import Confirm
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
        from rich.prompt import Confirm, Prompt
        if Confirm.ask("  DN đã có template hợp đồng/biểu mẫu riêng?", default=False):
            src = Prompt.ask("  Đường dẫn folder template (sẽ copy vào 00-Templates-Custom/)")
            src_path = Path(src).expanduser()
            if src_path.exists():
                _import_byot(src_path, vault_path / "00-Templates-Custom")
                console.print(f"  ✓ BYOT đã import từ {src_path}")

    # Init Git
    if non_interactive:
        do_git = True
    else:
        from rich.prompt import Confirm
        do_git = Confirm.ask("\n[bold]Init Git private repo cho vault?[/]", default=True)
    if do_git:
        try:
            from git import Repo
            if not (vault_path / ".git").exists():
                Repo.init(str(vault_path))
                console.print("  ✓ Git initialized")
        except Exception as e:
            console.print(f"  [yellow]⚠ Git init failed: {e}[/]")

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
