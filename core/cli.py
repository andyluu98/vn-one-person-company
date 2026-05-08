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
@click.argument("brief_arg", required=False, default=None)
@click.option("--brief", "brief_opt", default=None, help="Task brief (alternative to positional argument)")
@click.option("--vault", type=click.Path(), default=".", help="Vault path (default: current directory)")
def run(brief_arg, brief_opt, vault):
    """Chạy task qua orchestrator (Stage 1: brief → clarification).

    Cách dùng (cú pháp ngắn — khuyến nghị):
      vn-os run "Soạn HD lao động store manager 13tr"

    Hoặc cú pháp dài (backward compat):
      vn-os run --vault . --brief "Soạn HD lao động..."
    """
    from pathlib import Path
    from core.orchestrator.flow_controller import FlowController, FlowStage
    from core.llm.providers import get_default_provider

    # Resolve brief: positional arg ưu tiên, fallback --brief option
    brief = brief_arg or brief_opt
    if not brief:
        console.print("[red]✗ Thiếu brief. Dùng:[/]")
        console.print('  [cyan]vn-os run "Nội dung brief của bạn"[/]')
        console.print("Hoặc:")
        console.print('  [cyan]vn-os run --brief "Nội dung brief"[/]')
        return

    from core.utils.config import apply_vault_env_to_os
    vault_path = Path(vault)
    apply_vault_env_to_os(vault_path)
    fc = FlowController(vault_root=vault_path, llm=get_default_provider())
    result = fc.run(brief)

    if result.stage == FlowStage.PAUSE_CLARIFICATION:
        console.print(f"[yellow]⏸  Pause cho clarification[/]")
        console.print(f"   Folder: {result.task_folder}")
        console.print(f"   {result.message}")
        console.print(f"\n[bold]Bước tiếp:[/] mở {result.task_folder}/03-clarification.md, "
                      f"tick câu trả lời, lưu file. Rồi chạy:")
        console.print(f"  [cyan]vn-os resume {result.task_folder}[/]")
    elif result.stage == FlowStage.ERROR:
        console.print(f"[red]✗ {result.error}[/]")
    else:
        console.print(f"[green]→ {result.stage.value}[/]: {result.message}")


@main.command()
@click.argument("task_folder", type=click.Path(exists=True))
def resume(task_folder):
    """Resume flow sau khi CEO trả lời clarification."""
    from pathlib import Path
    from core.orchestrator.flow_controller import FlowController, FlowStage
    from core.llm.providers import get_default_provider

    from core.utils.config import apply_vault_env_to_os
    folder = Path(task_folder)
    vault_root = folder.parent.parent   # task_folder = vault/02-Tasks/<id>
    apply_vault_env_to_os(vault_root)

    fc = FlowController(vault_root=vault_root, llm=get_default_provider())
    result = fc.resume_after_clarification(folder)
    if result.stage == FlowStage.ERROR:
        console.print(f"[red]✗ {result.error}[/]")
    else:
        console.print(f"[cyan]Stage:[/] {result.stage.value}")
        console.print(f"   {result.message}")


@main.command()
@click.argument("task_folder", type=click.Path(exists=True))
def meeting(task_folder):
    """Sau khi CEO trả lời clarification → run meeting (Stop 1)."""
    from pathlib import Path
    import re
    from core.orchestrator.flow_controller import FlowController, FlowStage
    from core.llm.providers import get_default_provider

    from core.utils.config import apply_vault_env_to_os
    folder = Path(task_folder)
    apply_vault_env_to_os(folder.parent.parent)
    fc = FlowController(vault_root=folder.parent.parent, llm=get_default_provider())

    routing_md = (folder / "01-routing.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Departments:\*\* (.+)", routing_md)
    if not m:
        console.print("[red]✗ Cannot find Departments line in 01-routing.md[/]")
        return
    depts = [d.strip() for d in m.group(1).split(",")]

    result = fc.run_meeting(folder, departments=depts)
    console.print(f"[green]→ {result.stage.value}[/]: {result.message}")


@main.command()
@click.argument("task_folder", type=click.Path(exists=True))
def approve(task_folder):
    """CEO duyệt decision report → sinh execution plan."""
    from pathlib import Path
    from core.orchestrator.flow_controller import FlowController
    from core.llm.providers import get_default_provider

    from core.utils.config import apply_vault_env_to_os
    folder = Path(task_folder)
    apply_vault_env_to_os(folder.parent.parent)
    fc = FlowController(vault_root=folder.parent.parent, llm=get_default_provider())
    result = fc.approve_decision(folder)
    console.print(f"[green]{result.message}[/]")


@main.command(name="execute")
@click.argument("task_folder", type=click.Path(exists=True))
def execute_cmd(task_folder):
    """CEO duyệt execute → sinh .docx/.xlsx vào 03-Outputs/."""
    from pathlib import Path
    from core.orchestrator.flow_controller import FlowController
    from core.llm.providers import get_default_provider

    from core.utils.config import apply_vault_env_to_os
    folder = Path(task_folder)
    apply_vault_env_to_os(folder.parent.parent)
    fc = FlowController(vault_root=folder.parent.parent, llm=get_default_provider())
    result = fc.execute(folder)
    console.print(f"[green]→ DONE[/] {result.message}")


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


@main.command(name="install-mcp")
@click.option(
    "--vault",
    type=click.Path(exists=True, file_okay=False),
    help="Vault path để load .env (TAVILY_API_KEY, ...) inject vào MCP env",
)
@click.option(
    "--target",
    type=click.Choice(["desktop", "claude-code", "both"], case_sensitive=False),
    default="both",
    show_default=True,
    help="Host để đăng ký MCP server",
)
def install_mcp_cmd(vault, target):
    """Install vn-business-os as MCP server (Claude Desktop + Claude Code).

    Mặc định đăng ký vào cả hai. Dùng --target để chọn riêng.
    Sau khi install, restart Claude Desktop / Claude Code để load server.
    """
    from core.install_mcp import install_for_target
    from pathlib import Path

    results = install_for_target(
        target=target,
        vault_path=Path(vault) if vault else None,
    )

    for host, result in results.items():
        label = "Claude Desktop" if host == "desktop" else "Claude Code"
        if not result["ok"]:
            console.print(f"[red]✗ {label}: {result.get('error', 'install failed')}[/]")
            continue
        console.print(f"[green]✓ {label}:[/] {result['config_path']}")
        if result.get("backup"):
            console.print(f"   Backup: {result['backup']}")
        if result.get("env_keys_injected"):
            console.print(f"   Env injected: {', '.join(result['env_keys_injected'])}")

    targets_installed = [k for k, v in results.items() if v.get("ok")]
    if targets_installed:
        parts = []
        if "desktop" in targets_installed:
            parts.append("Claude Desktop")
        if "claude-code" in targets_installed:
            parts.append("Claude Code")
        console.print(f"\n[bold]Bước tiếp:[/] Restart {' + '.join(parts)} để load MCP server.")


@main.command(name="uninstall-mcp")
def uninstall_mcp_cmd():
    """Remove vn-business-os MCP server from Claude Desktop config."""
    from core.install_mcp import uninstall
    result = uninstall()
    if result.get("removed"):
        console.print(f"[green]✓ Removed MCP server entry from {result['config_path']}[/]")
    else:
        console.print(f"[yellow]→ Nothing to remove ({result.get('reason', 'unknown')})[/]")


if __name__ == "__main__":
    main()
