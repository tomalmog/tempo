# Tempo

**Automated Claude Code runner with rate limit handling.**

Run long-running Claude Code tasks overnight. Tempo automatically detects rate limits, waits for reset, and continues your task—no manual intervention required. Just start it and go to sleep.

## Features

- **🌙 True Overnight Automation** — Start a task, go to bed, wake up to results. Tempo handles everything automatically.
- **🔄 Smart Rate Limit Handling** — Parses Claude's exact reset time ("resets 4am") and waits until then + 1 minute
- **♻️ Multi-Cycle Support** — Runs through as many rate limit cycles as needed to complete your task
- **📝 Full Transcripts** — Every session is logged to markdown for later review
- **🎯 Sequence Mode** — Run multiple prompts in order, perfect for multi-step projects
- **💾 Crash Recovery** — Session state is saved, so you can resume if your machine restarts

## Installation

### macOS, Linux, WSL (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/tomalmog/tempo/main/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/tomalmog/tempo/main/install.ps1 | iex
```

### Using pip (requires Python)

```bash
pip install tempo-claude
```

### From source

```bash
git clone https://github.com/tomalmog/tempo
cd tempo
pip install -e .
```

## Quick Start

### Single Prompt

Run a single large task:

```bash
tempo run "Build a full-stack todo app with React, Express, PostgreSQL, and authentication"
```

Or from a file (useful for complex prompts):

```bash
tempo run --file ./my-big-task.md
```

### Sequence Mode

Run multiple prompts in order:

```bash
tempo run --sequence ./prompts.yaml
```

Example `prompts.yaml`:

```yaml
prompts:
  - name: "Project Setup"
    prompt: "Initialize a new React TypeScript project with Vite, Tailwind CSS, and ESLint"
  
  - name: "Authentication"
    prompt: "Add user authentication with JWT, including login, register, and protected routes"
  
  - name: "Dashboard"
    prompt: "Create a dashboard page with user stats, charts using Recharts, and a sidebar navigation"
  
  - name: "Testing"
    prompt: "Add comprehensive tests using Vitest and React Testing Library"
```

### Specify Project Directory

```bash
tempo run "Add dark mode support" --dir ./my-project
```

### Check Session Status

```bash
tempo status
```

### Clear Session (Start Fresh)

```bash
tempo clear
```

### Resume After Crash (Emergency Recovery)

If your machine crashes or restarts during a run, you can pick up where you left off:

```bash
tempo resume
```

Note: You shouldn't need this for normal operation—Tempo automatically waits and continues through rate limits.

## How It Works

1. **Injects a Completion Marker** — Tempo appends a system prompt telling Claude to output `<<<TEMPO_TASK_COMPLETE_7x9k2m>>>` when fully done

2. **Runs Claude in Print Mode** — Uses `claude --print --output-format stream-json` for clean, parseable output

3. **Monitors JSON Stream** — Watches for:
   - **Completion code** → Task done, move to next prompt or finish
   - **Rate limit** (e.g., "Spending cap reached resets 4am") → Parse time, wait, continue

4. **Waits Until Reset** — Parses the exact reset time and sleeps until then + 1 minute buffer. Shows a progress indicator so you know it's working.

5. **Continues Automatically** — After waiting, sends a "continue" prompt using `--continue` flag to pick up where Claude left off

6. **Loops Until Done** — Repeats steps 2-5 through as many rate limit cycles as needed

## Session Files

Tempo creates a `.tempo/` directory in your project:

```
.tempo/
├── .gitignore          # Ignores all tempo files
├── session.json        # Current session state
└── transcripts/
    └── 20240115_223045_abc123.md  # Full conversation log
```

Add `.tempo/` to your `.gitignore` if you want.

## CLI Reference

```
Usage: tempo [OPTIONS] COMMAND [ARGS]...

Commands:
  run     Run a task with Claude Code (main command)
  status  Show the status of the current session
  clear   Clear the current session
  resume  Resume after crash (emergency recovery only)

Run Options:
  PROMPT                    The prompt to send to Claude
  -f, --file PATH           Read prompt from a file
  -s, --sequence PATH       Run prompts from a YAML file
  -d, --dir PATH            Project directory (default: current)
  --no-skip-permissions     Don't use --dangerously-skip-permissions
  --force                   Start fresh even if session exists
  -v, --verbose             Verbose output
```

## Requirements

- Python 3.9+
- Claude Code CLI installed and authenticated
- Claude Pro subscription (for the rate-limited use case this solves)

## Authentication

Tempo uses your existing Claude Code authentication. Before using Tempo:

1. Make sure Claude Code is installed: `claude --version`
2. Run Claude once to authenticate: `claude "hello"` 
3. If you need to set up a token: `claude setup-token`

Tempo doesn't handle authentication itself—it just runs Claude CLI commands using your existing credentials.

## Tips

1. **Write detailed prompts** — The more context you give Claude, the better it will perform unattended

2. **Use sequence mode for complex projects** — Break your project into logical phases

3. **Check transcripts** — Review `.tempo/transcripts/` to see what Claude did overnight

4. **Set up your project first** — Tempo works best when Claude has a clear starting point (initialized repo, dependencies installed, etc.)

## Limitations

- Currently supports macOS and Linux (Windows support via WSL)
- Requires Claude Code Pro subscription
- Task detection relies on Claude outputting the completion code

## License

MIT

