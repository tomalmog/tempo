"""Core automation runner using Claude CLI."""

import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner

from tempo.config import (
    COMPLETION_CODE,
)
from tempo.parser import detect_completion, detect_rate_limit, parse_reset_time
from tempo.scheduler import wait_seconds_with_progress, wait_until_reset
from tempo.session import Session, SessionManager
from tempo.transcript import TranscriptWriter

console = Console()

# Default fallback wait time if we can't parse reset time (4.5 hours)
FALLBACK_WAIT_SECONDS = 4.5 * 60 * 60

# System prompt appended via --append-system-prompt
SYSTEM_PROMPT_APPEND = f"""

CRITICAL INSTRUCTION: When you have fully completed ALL tasks and there is absolutely nothing left to do, you MUST output this exact completion marker on its own line:

{COMPLETION_CODE}

Output this marker ONLY when you are 100% finished with everything requested. Do not output it prematurely."""


class TempoRunner:
    """
    Main runner that orchestrates Claude Code automation.
    
    Uses Claude CLI's --print mode with streaming JSON for clean automation:
    - Spawns Claude with structured output
    - Parses JSON events for progress, errors, rate limits
    - Waits for rate limit reset and continues with --continue flag
    - Persists session for crash recovery
    """
    
    def __init__(
        self,
        project_dir: str,
        skip_permissions: bool = True,
        verbose: bool = False,
    ):
        self.project_dir = Path(project_dir).resolve()
        self.skip_permissions = skip_permissions
        self.verbose = verbose
        
        self.session_manager = SessionManager(str(self.project_dir))
        self.session: Optional[Session] = None
        self.transcript: Optional[TranscriptWriter] = None
        
        # Buffer for accumulating output text
        self.output_buffer = ""
        
        # Flag for graceful shutdown
        self._shutdown_requested = False
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def handle_signal(signum, frame):
            self._shutdown_requested = True
            console.print("\n[yellow]Shutdown requested, saving session...[/yellow]")
            self._save_session()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
    
    def _build_command(self, prompt: str, is_continuation: bool = False) -> list:
        """Build the Claude CLI command."""
        cmd = ["claude"]
        
        # Use print mode for non-interactive operation
        cmd.extend(["--print"])
        
        # Use streaming JSON for parseable output (requires --verbose)
        cmd.extend(["--output-format", "stream-json", "--verbose"])
        
        # Skip permission prompts for unattended operation
        if self.skip_permissions:
            cmd.append("--dangerously-skip-permissions")
        
        # Add our system prompt for completion detection
        cmd.extend(["--append-system-prompt", SYSTEM_PROMPT_APPEND])
        
        # Continue previous conversation if resuming
        if is_continuation:
            cmd.append("--continue")
            # When continuing, ask Claude to proceed
            prompt = f"Continue working on the task. The previous session was interrupted by a rate limit. Pick up where you left off. Original task was: {prompt}"
        
        # Add the prompt
        cmd.append(prompt)
        
        return cmd
    
    def _run_claude(self, prompt: str, is_continuation: bool = False) -> tuple[str, bool, bool]:
        """
        Run Claude CLI and process output.
        
        Returns:
            (output_text, is_complete, is_rate_limited)
        """
        cmd = self._build_command(prompt, is_continuation)
        
        if self.verbose:
            console.print(f"[dim]Running: {' '.join(cmd[:5])}...[/dim]")
        
        self.output_buffer = ""
        is_complete = False
        is_rate_limited = False
        rate_limit_message = ""
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            
            # Process streaming JSON output
            for line in iter(process.stdout.readline, ''):
                if self._shutdown_requested:
                    process.terminate()
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Try to parse as JSON
                try:
                    event = json.loads(line)
                    event_type = event.get("type", "")
                    
                    # Handle different event types
                    if event_type == "assistant":
                        # Assistant message content
                        message = event.get("message", {})
                        content_blocks = message.get("content", [])
                        for block in content_blocks:
                            if block.get("type") == "text":
                                text = block.get("text", "")
                                self.output_buffer += text
                                console.print(text, end="")
                                
                                # Check for rate limit in assistant message
                                if detect_rate_limit(text):
                                    is_rate_limited = True
                                    rate_limit_message = text
                    
                    elif event_type == "content_block_delta":
                        # Streaming text delta
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            self.output_buffer += text
                            console.print(text, end="")
                    
                    elif event_type == "result":
                        # Final result - check is_error flag and result text
                        result_text = event.get("result", "")
                        is_error = event.get("is_error", False)
                        
                        if result_text:
                            if result_text not in self.output_buffer:
                                self.output_buffer += result_text
                                console.print(result_text, end="")
                            
                            # Check for rate limit in result
                            if is_error or detect_rate_limit(result_text):
                                if detect_rate_limit(result_text):
                                    is_rate_limited = True
                                    rate_limit_message = result_text
                    
                    elif event_type == "error":
                        # Error message - check for rate limit
                        error_msg = event.get("error", {})
                        error_text = str(error_msg)
                        console.print(f"\n[red]{error_text}[/red]")
                        
                        if detect_rate_limit(error_text):
                            is_rate_limited = True
                            rate_limit_message = error_text
                    
                    elif event_type == "system":
                        # System message
                        msg = event.get("message", "")
                        if self.verbose:
                            console.print(f"[dim]System: {event.get('subtype', '')}[/dim]")
                        
                        # Check for rate limit in system messages too
                        if detect_rate_limit(str(msg)):
                            is_rate_limited = True
                            rate_limit_message = str(msg)
                    
                except json.JSONDecodeError:
                    # Not JSON - might be plain text or error
                    self.output_buffer += line + "\n"
                    console.print(line)
                    
                    # Check for rate limit in plain text
                    if detect_rate_limit(line):
                        is_rate_limited = True
                        rate_limit_message = line
            
            process.wait()
            
            # Check for completion in final output
            if detect_completion(self.output_buffer):
                is_complete = True
            
            # Store rate limit message for parsing
            if is_rate_limited:
                self.output_buffer += f"\n{rate_limit_message}"
            
        except Exception as e:
            console.print(f"\n[red]Error running Claude: {e}[/red]")
            if self.verbose:
                import traceback
                console.print(traceback.format_exc())
        
        return self.output_buffer, is_complete, is_rate_limited
    
    def _save_session(self) -> None:
        """Save current session state."""
        if self.session:
            self.session.last_output_chunk = self.output_buffer[-2000:] if self.output_buffer else ""
            self.session_manager.save(self.session)
    
    def _handle_rate_limit(self, output: str) -> None:
        """Handle rate limit by waiting and preparing to resume."""
        self.session.status = "rate_limited"
        self.session.increment_cycle()
        self._save_session()
        
        rate_limit_info = parse_reset_time(output)
        
        if rate_limit_info:
            reset_time_str = rate_limit_info.reset_time.strftime("%I:%M %p %Z")
            
            if self.transcript:
                self.transcript.log_rate_limit(reset_time_str, self.session.cycle_count)
            
            wait_until_reset(rate_limit_info)
        else:
            # Couldn't parse reset time, use fallback
            console.print(
                "[yellow]Couldn't parse reset time, using fallback wait (4.5 hours)...[/yellow]"
            )
            if self.transcript:
                self.transcript.log_rate_limit("unknown (4.5h fallback)", self.session.cycle_count)
            
            wait_seconds_with_progress(
                FALLBACK_WAIT_SECONDS,
                "Waiting for rate limit reset...",
            )
        
        if self.transcript:
            self.transcript.log_resume()
    
    def run(
        self,
        prompt: Optional[str] = None,
        resume: bool = False,
    ) -> bool:
        """
        Run the automation loop.
        
        Args:
            prompt: The prompt to send to Claude (ignored if resuming)
            resume: Whether to resume an existing session
            
        Returns:
            True if completed successfully, False otherwise
        """
        self._setup_signal_handlers()
        
        # Load or create session
        if resume:
            self.session = self.session_manager.load()
            if not self.session:
                console.print("[red]No existing session found to resume.[/red]")
                return False
            console.print(f"[green]Resuming session {self.session.session_id}...[/green]")
            prompt = self.session.get_current_prompt()
        else:
            if not prompt:
                console.print("[red]No prompt provided.[/red]")
                return False
            
            # Check for existing session
            if self.session_manager.exists():
                existing = self.session_manager.load()
                if existing and existing.status not in ("completed", "failed"):
                    console.print(
                        f"[yellow]Existing session found ({existing.session_id}). "
                        f"Use --resume to continue or --force to start fresh.[/yellow]"
                    )
                    return False
            
            self.session = self.session_manager.create_new(prompt=prompt)
            console.print(f"[green]Created session {self.session.session_id}[/green]")
        
        # Create transcript
        self.transcript = TranscriptWriter(str(self.project_dir), self.session.session_id)
        
        # Print banner
        console.print(
            Panel(
                f"[bold]Tempo[/bold] - Automated Claude Code Runner\n\n"
                f"Session: {self.session.session_id}\n"
                f"Project: {self.project_dir}\n"
                f"Transcript: {self.transcript.get_path().name}",
                title="Starting",
                border_style="blue",
            )
        )
        
        is_continuation = self.session.cycle_count > 0 or resume
        original_prompt = self.session.get_current_prompt()
        
        # Main automation loop
        while not self._shutdown_requested:
            self.session.status = "running"
            self._save_session()
            
            if self.transcript:
                self.transcript.log_prompt(
                    original_prompt,
                    self.session.get_current_prompt_name(),
                )
            
            console.print(f"\n[blue]{'Continuing' if is_continuation else 'Sending'} prompt...[/blue]\n")
            console.print("─" * 60)
            
            # Run Claude
            output, is_complete, is_rate_limited = self._run_claude(
                original_prompt,
                is_continuation=is_continuation,
            )
            
            console.print("\n" + "─" * 60)
            
            # Log output
            if self.transcript:
                self.transcript.log_output(output)
            
            # Handle result
            if is_complete:
                has_more = self.session.mark_current_complete()
                self._save_session()
                
                if self.transcript:
                    self.transcript.log_complete(self.session.get_current_prompt_name())
                
                if has_more:
                    console.print(
                        f"\n[green]✓ Task complete. Moving to next prompt...[/green]"
                    )
                    is_continuation = False
                    original_prompt = self.session.get_current_prompt()
                    continue
                else:
                    console.print(
                        Panel(
                            "[bold green]All tasks completed![/bold green]\n\n"
                            f"Session: {self.session.session_id}\n"
                            f"Cycles: {self.session.cycle_count}\n"
                            f"Transcript: {self.transcript.get_path()}",
                            title="✅ Complete",
                            border_style="green",
                        )
                    )
                    if self.transcript:
                        self.transcript.log_session_end("completed")
                    return True
                    
            elif is_rate_limited:
                console.print("\n[yellow]Rate limit detected.[/yellow]")
                self._handle_rate_limit(output)
                is_continuation = True
                continue
                
            else:
                # Process exited without completion or rate limit
                # Could be an error or Claude just finished without the marker
                console.print(
                    "\n[yellow]Claude exited without completion marker.[/yellow]"
                )
                
                # Check if this looks like a successful completion anyway
                if "error" not in output.lower() and len(output) > 100:
                    console.print(
                        "[dim]Task may be complete - Claude didn't output the completion marker.\n"
                        "Use 'tempo resume' to continue, or 'tempo clear' to start fresh.[/dim]"
                    )
                
                self.session.status = "uncertain"
                self._save_session()
                
                if self.transcript:
                    self.transcript.log_error("Exited without completion marker")
                    self.transcript.log_session_end("uncertain")
                
                return False
        
        return False
    
    def run_sequence(self, prompts: list) -> bool:
        """
        Run a sequence of prompts.
        
        Args:
            prompts: List of PromptItem objects
            
        Returns:
            True if all prompts completed successfully
        """
        self._setup_signal_handlers()
        
        # Create session with prompt sequence
        self.session = self.session_manager.create_new(prompts=prompts)
        console.print(f"[green]Created sequence session {self.session.session_id}[/green]")
        console.print(f"[dim]Prompts: {len(prompts)}[/dim]")
        
        # Create transcript
        self.transcript = TranscriptWriter(str(self.project_dir), self.session.session_id)
        
        # Run using main loop
        return self.run(prompt=self.session.get_current_prompt())
