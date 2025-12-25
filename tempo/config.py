"""Configuration constants for Tempo."""

# The unique completion code that Claude will output when done
# This is injected via --append-system-prompt
COMPLETION_CODE = "<<<TEMPO_TASK_COMPLETE_7x9k2m>>>"

# Patterns to detect rate limiting
RATE_LIMIT_PATTERNS = [
    r"Limit reached",
    r"rate limit",
    r"usage limit",
    r"too many requests",
    r"Internal error.*Limit",
    r"Spending cap reached",
    r"spending cap",
]

# Patterns to extract reset time from Claude's message
# Format 1: "resets 4am (America/Toronto)" - with timezone
# Format 2: "resets 4am" - without timezone (uses local)
RESET_TIME_PATTERN_WITH_TZ = r"resets\s+(\d{1,2}(?::\d{2})?(?:am|pm)?)\s+\(([^)]+)\)"
RESET_TIME_PATTERN_NO_TZ = r"resets\s+(\d{1,2}(?::\d{2})?(?:am|pm)?)"

# Buffer time (seconds) to add after reset time before retrying
RESET_BUFFER_SECONDS = 60

# Session file location (relative to project directory)
SESSION_DIR = ".tempo"
SESSION_FILE = "session.json"
TRANSCRIPT_DIR = "transcripts"
