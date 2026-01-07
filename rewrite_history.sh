#!/bin/bash

# Rewrite git history to spread commits over 2 weeks
# Run from repo root

set -e

echo "This will REWRITE your git history. Make sure you have a backup."
echo "Press Enter to continue or Ctrl+C to abort..."
read

# Store current branch
BRANCH=$(git branch --show-current)

# Create a new orphan branch
git checkout --orphan temp_branch

# Remove all files from staging
git rm -rf --cached . 2>/dev/null || true

# Base date: 2 weeks ago
BASE_DATE="2025-12-24"

commit_with_date() {
    local date="$1"
    local time="$2"
    local msg="$3"
    
    export GIT_AUTHOR_DATE="$date $time -0500"
    export GIT_COMMITTER_DATE="$date $time -0500"
    git commit -m "$msg"
    unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE
}

# Commit 1 - Dec 24 morning - Initial setup
git add pyproject.toml
git add tempo/__init__.py
commit_with_date "2025-12-24" "09:23:41" "initial project setup"

# Commit 2 - Dec 24 afternoon - Config
git add tempo/config.py
commit_with_date "2025-12-24" "14:17:22" "add config with completion code and rate limit patterns"

# Commit 3 - Dec 25 - Parser basics
git add tempo/parser.py
commit_with_date "2025-12-25" "11:45:33" "basic rate limit detection"

# Commit 4 - Dec 26 - Scheduler
git add tempo/scheduler.py
commit_with_date "2025-12-26" "16:02:18" "add scheduler for waiting until reset time"

# Commit 5 - Dec 26 evening - Session management
git add tempo/session.py
commit_with_date "2025-12-26" "20:31:45" "session state persistence"

# Commit 6 - Dec 27 - Transcript logging
git add tempo/transcript.py
commit_with_date "2025-12-27" "10:14:27" "transcript logging to markdown"

# Commit 7 - Dec 27 afternoon - Core runner
git add tempo/runner.py
commit_with_date "2025-12-27" "15:48:52" "core runner implementation"

# Commit 8 - Dec 28 - CLI
git add tempo/cli.py
git add tempo/__main__.py
commit_with_date "2025-12-28" "12:33:16" "cli with click"

# Commit 9 - Dec 28 - Entry point fix
git add -A tempo/
commit_with_date "2025-12-28" "13:41:29" "fix module entry point"

# Commit 10 - Dec 29 - README
git add README.md
commit_with_date "2025-12-29" "09:55:44" "add readme"

# Commit 11 - Dec 30 - Examples
git add examples/
commit_with_date "2025-12-30" "14:22:31" "add example prompts"

# Commit 12 - Dec 31 - PyInstaller spec
git add tempo.spec
commit_with_date "2025-12-31" "11:08:17" "pyinstaller config for standalone binary"

# Commit 13 - Jan 1 - Installers
git add install.sh
git add install.ps1
git add install.cmd
commit_with_date "2026-01-01" "16:44:53" "add installer scripts"

# Commit 14 - Jan 2 - GitHub Actions
git add .github/workflows/release.yml
commit_with_date "2026-01-02" "10:27:38" "github actions for releases"

# Commit 15 - Jan 2 afternoon - Test workflow
git add .github/workflows/test.yml
commit_with_date "2026-01-02" "15:19:42" "add test workflow"

# Commit 16 - Jan 3 - Scripts folder
git add scripts/
commit_with_date "2026-01-03" "09:12:55" "local build test script"

# Commit 17 - Jan 3 - Gitignore
git add .gitignore
commit_with_date "2026-01-03" "09:45:23" "gitignore"

# Commit 18 - Jan 4 - Website init
git add website/package.json
git add website/tsconfig.json
git add website/next.config.js
git add website/tailwind.config.js
git add website/postcss.config.js
commit_with_date "2026-01-04" "11:33:47" "init landing page"

# Commit 19 - Jan 4 afternoon - Website layout
git add website/app/layout.tsx
git add website/app/globals.css
commit_with_date "2026-01-04" "14:58:21" "base layout and styles"

# Commit 20 - Jan 5 - Landing page components
git add website/app/page.tsx
git add website/app/components/
commit_with_date "2026-01-05" "10:42:16" "landing page components"

# Commit 21 - Jan 5 - API routes
git add website/app/api/
commit_with_date "2026-01-05" "16:27:33" "api routes"

# Commit 22 - Jan 6 - Redis integration
git add website/lib/
commit_with_date "2026-01-06" "11:15:48" "redis for download tracking"

# Commit 23 - Jan 6 - Logo
git add website/public/
commit_with_date "2026-01-06" "14:33:22" "add logo"

# Commit 24 - Jan 7 morning - Design spec
git add design/
commit_with_date "2026-01-07" "08:41:17" "design spec"

# Commit 25 - Jan 7 - Final touches (add any remaining files)
git add -A
git add tempologo.png 2>/dev/null || true
# Check if there are staged changes
if git diff --cached --quiet; then
    echo "No additional files to commit"
else
    commit_with_date "2026-01-07" "10:22:54" "cleanup"
fi

# Replace main branch
git branch -D "$BRANCH" 2>/dev/null || true
git branch -m "$BRANCH"

echo ""
echo "Done! History rewritten with 25 commits over 2 weeks."
echo "Run 'git log --oneline' to verify."
echo ""
echo "To push: git push --force origin $BRANCH"

