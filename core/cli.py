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
    console.print("[yellow]TODO Phase 1 Task 10:[/] CLI status stub")


@main.command()
@click.option("--brief", required=True, help="Task brief (Vietnamese)")
@click.option("--vault", type=click.Path(), default=".")
def run(brief, vault):
    """Chạy task qua orchestrator."""
    console.print(f"[yellow]TODO Phase 3:[/] sẽ kết nối orchestrator")


@main.command()
def onboard():
    """Wizard tạo vault mới."""
    console.print("[yellow]TODO Phase 6:[/] onboard wizard")


if __name__ == "__main__":
    main()
