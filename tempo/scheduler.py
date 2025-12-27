"""Scheduling utilities for waiting until reset time."""

import time
from datetime import datetime, timedelta
from typing import Optional

from dateutil import tz
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from tempo.config import RESET_BUFFER_SECONDS
from tempo.parser import RateLimitInfo

console = Console()


def calculate_wait_seconds(rate_limit_info: RateLimitInfo) -> float:
    """
    Calculate seconds to wait until reset time plus buffer.
    
    Args:
        rate_limit_info: Parsed rate limit information with reset time
        
    Returns:
        Number of seconds to wait (minimum 0)
    """
    now = datetime.now(rate_limit_info.reset_time.tzinfo)
    wait_delta = rate_limit_info.reset_time - now
    wait_seconds = wait_delta.total_seconds() + RESET_BUFFER_SECONDS
    
    return max(0, wait_seconds)


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def wait_until_reset(
    rate_limit_info: RateLimitInfo,
    check_interval: float = 60.0,
) -> None:
    """
    Wait until the rate limit resets.
    
    Displays a progress indicator and periodically logs status.
    
    Args:
        rate_limit_info: Parsed rate limit information
        check_interval: Seconds between status updates
    """
    wait_seconds = calculate_wait_seconds(rate_limit_info)
    
    if wait_seconds <= 0:
        console.print("[green]Reset time has passed, continuing immediately...[/green]")
        return
    
    reset_time_str = rate_limit_info.reset_time.strftime("%I:%M %p")
    console.print(
        f"\n[yellow]⏳ Rate limited. Waiting until {reset_time_str} "
        f"({rate_limit_info.timezone_name})[/yellow]"
    )
    console.print(f"[dim]Total wait: {format_duration(wait_seconds)}[/dim]\n")
    
    start_time = time.time()
    end_time = start_time + wait_seconds
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Waiting for rate limit reset...", total=None)
        
        while time.time() < end_time:
            remaining = end_time - time.time()
            progress.update(
                task,
                description=f"Waiting... {format_duration(remaining)} remaining",
            )
            
            # Sleep in intervals so we can update the display
            sleep_time = min(check_interval, remaining)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    console.print("[green]✓ Wait complete, resuming...[/green]\n")


def wait_seconds_with_progress(seconds: float, message: str = "Waiting...") -> None:
    """
    Wait for a specified number of seconds with progress display.
    
    Useful for fixed waits (e.g., fallback when we can't parse reset time).
    """
    if seconds <= 0:
        return
    
    console.print(f"\n[yellow]⏳ {message}[/yellow]")
    console.print(f"[dim]Duration: {format_duration(seconds)}[/dim]\n")
    
    start_time = time.time()
    end_time = start_time + seconds
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(message, total=None)
        
        while time.time() < end_time:
            remaining = end_time - time.time()
            progress.update(
                task,
                description=f"{message} {format_duration(remaining)} remaining",
            )
            
            sleep_time = min(60.0, remaining)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    console.print("[green]✓ Wait complete[/green]\n")

