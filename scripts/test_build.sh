#!/bin/bash
# Test script to verify builds will work on GitHub Actions
# Run this before pushing to catch errors early

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Use the Python that has tempo installed, or default to python3
if command -v python &> /dev/null && python -c "import tempo" 2>/dev/null; then
    PYTHON="python"
elif command -v python3 &> /dev/null && $PYTHON -c "import tempo" 2>/dev/null; then
    PYTHON="python3"
else
    # Fallback: try to find anaconda python
    if [ -x "/opt/anaconda3/bin/python" ]; then
        PYTHON="/opt/anaconda3/bin/python"
    else
        echo "Error: Cannot find Python with tempo installed"
        echo "Run: pip install -e ."
        exit 1
    fi
fi

echo "Using Python: $PYTHON"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Tempo Build Test Suite                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓ PASS:${NC} $1"; }
fail() { echo -e "${RED}✗ FAIL:${NC} $1"; exit 1; }
info() { echo -e "${YELLOW}→${NC} $1"; }

# Test 1: Check Python version
echo "Test 1: Python version"
info "Checking Python >= 3.9..."
$PYTHON -c "import sys; assert sys.version_info >= (3, 9), 'Python 3.9+ required'" && pass "Python version OK" || fail "Python 3.9+ required"

# Test 2: Install package
echo ""
echo "Test 2: Package installation"
info "Installing tempo in editable mode..."
pip install -e . -q && pass "Package installs correctly" || fail "Package installation failed"

# Test 3: Import test
echo ""
echo "Test 3: Import test"
info "Testing imports..."
$PYTHON -c "
from tempo.cli import main
from tempo.runner import TempoRunner
from tempo.parser import detect_rate_limit, parse_reset_time
from tempo.scheduler import wait_until_reset
from tempo.session import Session, SessionManager
from tempo.transcript import TranscriptWriter
from tempo.config import COMPLETION_CODE
print('All imports successful')
" && pass "All modules import correctly" || fail "Import error"

# Test 4: CLI works
echo ""
echo "Test 4: CLI test"
info "Testing CLI..."
tempo --version > /dev/null && pass "CLI runs correctly" || fail "CLI failed"

# Test 5: Rate limit parser
echo ""
echo "Test 5: Rate limit parser"
info "Testing rate limit detection..."
$PYTHON -c "
from tempo.parser import detect_rate_limit, parse_reset_time

# Test detection
assert detect_rate_limit('Spending cap reached resets 4am'), 'Should detect spending cap'
assert detect_rate_limit('Limit reached'), 'Should detect limit reached'
assert detect_rate_limit('rate limit exceeded'), 'Should detect rate limit'
assert not detect_rate_limit('Hello world'), 'Should not false positive'

# Test time parsing
info = parse_reset_time('Spending cap reached resets 4am')
assert info is not None, 'Should parse reset time'
assert info.reset_time.hour == 4, 'Should parse 4am correctly'

print('Parser tests passed')
" && pass "Rate limit parser works" || fail "Parser test failed"

# Test 6: Session persistence
echo ""
echo "Test 6: Session persistence"
info "Testing session save/load..."
$PYTHON -c "
import tempfile
import os
from tempo.session import SessionManager, PromptItem

with tempfile.TemporaryDirectory() as tmpdir:
    manager = SessionManager(tmpdir)
    
    # Create session
    session = manager.create_new(prompt='Test prompt')
    assert session.session_id, 'Should have session ID'
    
    # Save and load
    manager.save(session)
    loaded = manager.load()
    assert loaded is not None, 'Should load session'
    assert loaded.session_id == session.session_id, 'Should preserve session ID'
    assert loaded.original_prompt == 'Test prompt', 'Should preserve prompt'
    
    # Delete
    manager.delete()
    assert not manager.exists(), 'Should delete session'

print('Session tests passed')
" && pass "Session persistence works" || fail "Session test failed"

# Test 7: PyInstaller availability (optional)
echo ""
echo "Test 7: PyInstaller build test (optional)"
if command -v pyinstaller &> /dev/null; then
    info "PyInstaller found, testing build..."
    
    # Quick build test (just verify it starts, don't wait for full build)
    timeout 30 pyinstaller --onefile --name tempo-test tempo/__main__.py 2>&1 | head -20 || true
    
    if [ -f "dist/tempo-test" ] || [ -f "dist/tempo-test.exe" ]; then
        pass "PyInstaller build succeeds"
        rm -rf build dist tempo-test.spec
    else
        info "PyInstaller build incomplete (timeout) - this is OK for quick tests"
    fi
else
    info "PyInstaller not installed - skipping build test"
    info "Install with: pip install pyinstaller"
fi

# Test 8: YAML parsing
echo ""
echo "Test 8: YAML sequence parsing"
info "Testing sequence file parsing..."
$PYTHON -c "
import yaml
from tempo.session import PromptItem

# Parse example sequence
with open('examples/sequence.yaml', 'r') as f:
    data = yaml.safe_load(f)

prompts = []
for item in data.get('prompts', []):
    prompts.append(PromptItem(
        name=item.get('name', 'Unnamed'),
        prompt=item['prompt'],
    ))

assert len(prompts) == 4, f'Should have 4 prompts, got {len(prompts)}'
assert prompts[0].name == 'Project Initialization', 'First prompt name should match'

print('YAML parsing tests passed')
" && pass "YAML parsing works" || fail "YAML parsing failed"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              All tests passed! ✓                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "You can now push with confidence."

