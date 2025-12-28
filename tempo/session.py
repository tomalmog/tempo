"""Session persistence for crash recovery and state tracking."""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tempo.config import SESSION_DIR, SESSION_FILE


@dataclass
class PromptItem:
    """A single prompt in a sequence."""
    
    name: str
    prompt: str
    completed: bool = False
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Session:
    """Persistent session state."""
    
    # Unique session identifier
    session_id: str
    
    # Project directory being worked on
    project_dir: str
    
    # Original prompt (for single-prompt mode)
    original_prompt: Optional[str] = None
    
    # Sequence of prompts (for sequence mode)
    prompts: List[PromptItem] = field(default_factory=list)
    
    # Current prompt index in sequence (-1 for single-prompt mode)
    current_prompt_index: int = -1
    
    # Number of rate limit cycles completed
    cycle_count: int = 0
    
    # Session timestamps
    created_at: str = ""
    updated_at: str = ""
    
    # Current status
    status: str = "pending"  # pending, running, rate_limited, completed, failed
    
    # Last output chunk (for context when resuming)
    last_output_chunk: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def get_current_prompt(self) -> str:
        """Get the current prompt to send to Claude."""
        if self.current_prompt_index >= 0 and self.prompts:
            return self.prompts[self.current_prompt_index].prompt
        return self.original_prompt or ""
    
    def get_current_prompt_name(self) -> str:
        """Get the name of the current prompt."""
        if self.current_prompt_index >= 0 and self.prompts:
            return self.prompts[self.current_prompt_index].name
        return "main"
    
    def mark_current_complete(self) -> bool:
        """
        Mark the current prompt as complete and advance.
        
        Returns True if there are more prompts, False if done.
        """
        self.updated_at = datetime.now().isoformat()
        
        if self.current_prompt_index >= 0 and self.prompts:
            self.prompts[self.current_prompt_index].completed = True
            self.prompts[self.current_prompt_index].completed_at = datetime.now().isoformat()
            
            # Check if there are more prompts
            if self.current_prompt_index < len(self.prompts) - 1:
                self.current_prompt_index += 1
                self.prompts[self.current_prompt_index].started_at = datetime.now().isoformat()
                return True
        
        # No more prompts or single-prompt mode
        self.status = "completed"
        return False
    
    def increment_cycle(self) -> None:
        """Increment the rate limit cycle count."""
        self.cycle_count += 1
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        # Handle prompts specially
        prompts_data = data.pop("prompts", [])
        prompts = [PromptItem(**p) for p in prompts_data]
        return cls(prompts=prompts, **data)


class SessionManager:
    """Manages session persistence to disk."""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        self.session_dir = self.project_dir / SESSION_DIR
        self.session_file = self.session_dir / SESSION_FILE
    
    def _ensure_dir(self) -> None:
        """Ensure the session directory exists."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Add .gitignore to session directory
        gitignore = self.session_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n")
    
    def save(self, session: Session) -> None:
        """Save session to disk."""
        self._ensure_dir()
        session.updated_at = datetime.now().isoformat()
        
        with open(self.session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def load(self) -> Optional[Session]:
        """Load session from disk if it exists."""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, "r") as f:
                data = json.load(f)
            return Session.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def exists(self) -> bool:
        """Check if a session file exists."""
        return self.session_file.exists()
    
    def delete(self) -> None:
        """Delete the session file."""
        if self.session_file.exists():
            self.session_file.unlink()
    
    def create_new(
        self,
        prompt: Optional[str] = None,
        prompts: Optional[List[PromptItem]] = None,
    ) -> Session:
        """
        Create a new session.
        
        Args:
            prompt: Single prompt (for single-prompt mode)
            prompts: List of prompts (for sequence mode)
        """
        import uuid
        
        session = Session(
            session_id=str(uuid.uuid4())[:8],
            project_dir=str(self.project_dir),
            original_prompt=prompt,
            prompts=prompts or [],
            current_prompt_index=0 if prompts else -1,
            status="pending",
        )
        
        if prompts:
            prompts[0].started_at = datetime.now().isoformat()
        
        self.save(session)
        return session

