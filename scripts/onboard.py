"""Onboarding wizard CLI — wraps core.onboard library.

Pure Python lib lives in core/onboard.py — this is just a CLI front-end
for interactive wizard / non-interactive mode.
"""
from __future__ import annotations
import sys
from pathlib import Path

import click
from rich.console import Console

# Allow running this script directly: ensure repo root on sys.path so `core` imports.
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from core.onboard import onboard_vault  # noqa: E402

console = Console()


@click.command()
@click.option("--vault", type=click.Path(), required=True, help="Vault destination")
@click.option("--non-interactive", is_flag=True, help="Skip prompts (for CI/MCP)")
@click.option("--pack", multiple=True, help="Pack code(s) to install")
def main(vault, non_interactive, pack):
    """Onboard wizard: tạo vault + chọn pack + import template DN."""
    vault_path = Path(vault).expanduser().resolve()
    selected_packs = list(pack)
    byot_src = None

    if vault_path.exists() and any(vault_path.iterdir()):
        if not non_interactive:
            from rich.prompt import Confirm
            if not Confirm.ask(
                f"⚠️  {vault_path} đã có dữ liệu. Tiếp tục? (sẽ ghi đè)"
            ):
                console.print("[red]Hủy.[/]")
                return

    # Interactive pack selection
    if not non_interactive and not selected_packs:
        from rich.prompt import Confirm, Prompt

        for code, name in [
            ("fnb", "F&B (quán ăn/cafe/nhà hàng)"),
            ("retail", "Retail (shop/e-commerce/D2C)"),
            ("tech-saas", "Tech/SaaS (startup phần mềm)"),
        ]:
            if Confirm.ask(f"  Cài pack {name}?", default=False):
                selected_packs.append(code)

        if Confirm.ask(
            "  DN đã có template hợp đồng/biểu mẫu riêng?", default=False
        ):
            byot_src = Prompt.ask(
                "  Đường dẫn folder template (sẽ copy vào 00-Templates-Custom/)"
            )

    # Run onboard via lib
    console.print("[bold]Đang tạo vault...[/]")
    result = onboard_vault(
        vault_path=vault_path,
        packs=selected_packs,
        byot_src=byot_src,
        init_git=True,
    )

    if not result.get("ok"):
        console.print(f"[red]✗ {result.get('error', 'unknown error')}[/]")
        sys.exit(1)

    for step in result.get("steps", []):
        console.print(f"  ✓ {step}")
    for w in result.get("warnings", []):
        console.print(f"  [yellow]⚠ {w}[/]")

    console.print(f"\n[green]✅ Vault sẵn sàng tại {result['vault']}[/]")
    console.print("[bold]Bước tiếp:[/]")
    for s in result.get("next_steps", []):
        console.print(f"  - {s}")


# Backwards-compat shims: existing test imports `_install_pack` from this module.
from core.onboard import (  # noqa: E402, F401
    _install_departments,
    _install_pack,
    _import_byot,
)


if __name__ == "__main__":
    main()
