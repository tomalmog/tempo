"""Transcript logging for session history."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from tempo.config import SESSION_DIR, TRANSCRIPT_DIR


class TranscriptWriter:
    """Writes conversation transcripts to disk."""
    
    def __init__(self, project_dir: str, session_id: str):
        self.project_dir = Path(project_dir).resolve()
        self.session_id = session_id
        self.transcript_dir = self.project_dir / SESSION_DIR / TRANSCRIPT_DIR
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.transcript_file = self.transcript_dir / f"{timestamp}_{session_id}.md"
        
        self._ensure_dir()
        self._write_header()
    
    def _ensure_dir(self) -> None:
        """Ensure the transcript directory exists."""
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
    
    def _write_header(self) -> None:
        """Write the transcript header."""
        header = f"""# Tempo Session Transcript

**Session ID:** {self.session_id}
**Started:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Project:** {self.project_dir}

---

"""
        with open(self.transcript_file, "w") as f:
            f.write(header)
    
    def log_prompt(self, prompt: str, prompt_name: Optional[str] = None) -> None:
        """Log a prompt sent to Claude."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        name_str = f" ({prompt_name})" if prompt_name else ""
        
        entry = f"""
## Prompt{name_str} - {timestamp}

```
{prompt}
```

"""
        self._append(entry)
    
    def log_output(self, output: str) -> None:
        """Log Claude's output."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = f"""
## Claude Output - {timestamp}

{output}

"""
        self._append(entry)
    
    def log_rate_limit(self, reset_time: str, cycle: int) -> None:
        """Log a rate limit event."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = f"""
---

**⏳ Rate Limited** - {timestamp}
- Cycle: {cycle}
- Reset time: {reset_time}
- Waiting...

---

"""
        self._append(entry)
    
    def log_resume(self) -> None:
        """Log resuming after rate limit."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = f"""
---

**✓ Resumed** - {timestamp}

---

"""
        self._append(entry)
    
    def log_complete(self, prompt_name: Optional[str] = None) -> None:
        """Log task completion."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        name_str = f" ({prompt_name})" if prompt_name else ""
        
        entry = f"""
---

**✅ Task Complete{name_str}** - {timestamp}

---

"""
        self._append(entry)
    
    def log_error(self, error: str) -> None:
        """Log an error."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = f"""
---

**❌ Error** - {timestamp}

```
{error}
```

---

"""
        self._append(entry)
    
    def log_session_end(self, status: str) -> None:
        """Log session end."""
        entry = f"""
---

# Session Ended

**Status:** {status}
**Ended:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        self._append(entry)
    
    def _append(self, content: str) -> None:
        """Append content to the transcript file."""
        with open(self.transcript_file, "a") as f:
            f.write(content)
    
    def get_path(self) -> Path:
        """Get the transcript file path."""
        return self.transcript_file

