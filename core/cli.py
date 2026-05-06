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
    """Chạy task qua orchestrator (Stage 1: brief → clarification)."""
    from pathlib import Path
    from core.orchestrator.flow_controller import FlowController, FlowStage
    from core.llm.providers import get_default_provider

    fc = FlowController(vault_root=Path(vault), llm=get_default_provider())
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

    folder = Path(task_folder)
    vault_root = folder.parent.parent   # task_folder = vault/02-Tasks/<id>

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

    folder = Path(task_folder)
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

    folder = Path(task_folder)
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

    folder = Path(task_folder)
    fc = FlowController(vault_root=folder.parent.parent, llm=get_default_provider())
    result = fc.execute(folder)
    console.print(f"[green]→ DONE[/] {result.message}")


@main.command()
def onboard():
    """Wizard tạo vault mới."""
    console.print(f"[yellow]TODO Phase 6:[/] onboard wizard")


if __name__ == "__main__":
    main()
