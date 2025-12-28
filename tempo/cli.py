"""Command-line interface for Tempo."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tempo import __version__
from tempo.runner import TempoRunner
from tempo.session import PromptItem, SessionManager

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="tempo")
def main():
    """
    Tempo - Automated Claude Code runner with rate limit handling.
    
    Run long-running Claude Code tasks overnight. Tempo automatically
    detects rate limits, waits for reset, and continues your task.
    """
    pass


@main.command()
@click.argument("prompt", required=False)
@click.option(
    "--file", "-f",
    type=click.Path(exists=True),
    help="Read prompt from a file instead of command line.",
)
@click.option(
    "--sequence", "-s",
    type=click.Path(exists=True),
    help="Run a sequence of prompts from a YAML file.",
)
@click.option(
    "--dir", "-d",
    type=click.Path(exists=True),
    default=".",
    help="Project directory to run Claude in. Defaults to current directory.",
)
@click.option(
    "--no-skip-permissions",
    is_flag=True,
    help="Don't use --dangerously-skip-permissions flag.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force start a new session even if one exists.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output.",
)
def run(
    prompt: Optional[str],
    file: Optional[str],
    sequence: Optional[str],
    dir: str,
    no_skip_permissions: bool,
    force: bool,
    verbose: bool,
):
    """
    Run a task with Claude Code.
    
    Provide a prompt directly, from a file, or as a sequence.
    
    \b
    Examples:
        tempo run "Build a REST API with authentication"
        tempo run --file ./my-task.md
        tempo run --sequence ./prompts.yaml
        tempo run "Add tests" --dir ./my-project
    """
    project_dir = Path(dir).resolve()
    
    # Validate inputs
    if sequence:
        # Sequence mode
        prompts = _load_sequence(sequence)
        if not prompts:
            console.print("[red]Failed to load sequence file.[/red]")
            sys.exit(1)
        
        runner = TempoRunner(
            str(project_dir),
            skip_permissions=not no_skip_permissions,
            verbose=verbose,
        )
        
        if force:
            runner.session_manager.delete()
        
        success = runner.run_sequence(prompts)
        sys.exit(0 if success else 1)
        
    elif file:
        # Read prompt from file
        prompt = Path(file).read_text().strip()
        
    elif not prompt:
        console.print("[red]Please provide a prompt, --file, or --sequence.[/red]")
        console.print("[dim]Use 'tempo run --help' for usage.[/dim]")
        sys.exit(1)
    
    # Handle existing session
    session_manager = SessionManager(str(project_dir))
    if not force and session_manager.exists():
        existing = session_manager.load()
        if existing and existing.status not in ("completed", "failed"):
            console.print(
                Panel(
                    f"[yellow]Existing session found[/yellow]\n\n"
                    f"Session ID: {existing.session_id}\n"
                    f"Status: {existing.status}\n"
                    f"Cycles: {existing.cycle_count}\n\n"
                    f"Use [bold]tempo resume[/bold] to continue this session,\n"
                    f"or [bold]tempo run --force[/bold] to start fresh.",
                    title="Session Exists",
                    border_style="yellow",
                )
            )
            sys.exit(1)
    
    # Run
    runner = TempoRunner(
        str(project_dir),
        skip_permissions=not no_skip_permissions,
        verbose=verbose,
    )
    
    if force:
        runner.session_manager.delete()
    
    success = runner.run(prompt=prompt)
    sys.exit(0 if success else 1)


@main.command()
@click.option(
    "--dir", "-d",
    type=click.Path(exists=True),
    default=".",
    help="Project directory. Defaults to current directory.",
)
@click.option(
    "--no-skip-permissions",
    is_flag=True,
    help="Don't use --dangerously-skip-permissions flag.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output.",
)
def resume(dir: str, no_skip_permissions: bool, verbose: bool):
    """
    Resume after a crash (emergency recovery).
    
    Only needed if your machine crashed or restarted during a run.
    Normal rate limit handling is automatic—you don't need this
    for regular overnight runs.
    """
    project_dir = Path(dir).resolve()
    
    runner = TempoRunner(
        str(project_dir),
        skip_permissions=not no_skip_permissions,
        verbose=verbose,
    )
    
    success = runner.run(resume=True)
    sys.exit(0 if success else 1)


@main.command()
@click.option(
    "--dir", "-d",
    type=click.Path(exists=True),
    default=".",
    help="Project directory. Defaults to current directory.",
)
def status(dir: str):
    """
    Show the status of the current session.
    """
    project_dir = Path(dir).resolve()
    session_manager = SessionManager(str(project_dir))
    
    if not session_manager.exists():
        console.print("[dim]No active session in this directory.[/dim]")
        return
    
    session = session_manager.load()
    if not session:
        console.print("[red]Could not load session.[/red]")
        return
    
    # Build status table
    table = Table(title="Session Status", show_header=False, box=None)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    
    table.add_row("Session ID", session.session_id)
    table.add_row("Status", _format_status(session.status))
    table.add_row("Project", session.project_dir)
    table.add_row("Created", session.created_at)
    table.add_row("Updated", session.updated_at)
    table.add_row("Rate Limit Cycles", str(session.cycle_count))
    
    if session.prompts:
        completed = sum(1 for p in session.prompts if p.completed)
        table.add_row("Prompts", f"{completed}/{len(session.prompts)} complete")
    
    console.print(table)
    
    # Show prompts if in sequence mode
    if session.prompts:
        console.print("\n[bold]Prompt Sequence:[/bold]")
        for i, prompt in enumerate(session.prompts):
            status_icon = "✓" if prompt.completed else ("→" if i == session.current_prompt_index else "○")
            status_style = "green" if prompt.completed else ("yellow" if i == session.current_prompt_index else "dim")
            console.print(f"  [{status_style}]{status_icon} {prompt.name}[/{status_style}]")


@main.command()
@click.option(
    "--dir", "-d",
    type=click.Path(exists=True),
    default=".",
    help="Project directory. Defaults to current directory.",
)
@click.confirmation_option(prompt="Are you sure you want to clear the session?")
def clear(dir: str):
    """
    Clear the current session.
    
    Removes session state, allowing you to start fresh.
    """
    project_dir = Path(dir).resolve()
    session_manager = SessionManager(str(project_dir))
    
    if session_manager.exists():
        session_manager.delete()
        console.print("[green]Session cleared.[/green]")
    else:
        console.print("[dim]No session to clear.[/dim]")


def _format_status(status: str) -> str:
    """Format status with color."""
    colors = {
        "pending": "dim",
        "running": "blue",
        "rate_limited": "yellow",
        "completed": "green",
        "failed": "red",
        "uncertain": "yellow",
    }
    color = colors.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def _load_sequence(path: str) -> list:
    """Load a sequence of prompts from a YAML file."""
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        prompts = []
        for item in data.get("prompts", []):
            prompts.append(PromptItem(
                name=item.get("name", f"Step {len(prompts) + 1}"),
                prompt=item["prompt"],
            ))
        
        return prompts
        
    except Exception as e:
        console.print(f"[red]Error loading sequence: {e}[/red]")
        return []


if __name__ == "__main__":
    main()

