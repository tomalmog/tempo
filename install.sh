#!/usr/bin/env bash
# Tempo Installer for macOS, Linux, and WSL
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/tempo/main/install.sh | bash

set -e

# Configuration
REPO="tomalmog/tempo"
INSTALL_DIR="${TEMPO_INSTALL_DIR:-$HOME/.local/bin}"
BINARY_NAME="tempo"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}"
    echo "  ╔════════════════════════════════════════╗"
    echo "  ║           Tempo Installer              ║"
    echo "  ║   Automated Claude Code Runner         ║"
    echo "  ╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

warn() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

error() {
    echo -e "${RED}ERROR:${NC} $1"
    exit 1
}

detect_platform() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    case "$os" in
        darwin)
            OS="macos"
            ;;
        linux)
            OS="linux"
            ;;
        mingw*|msys*|cygwin*)
            error "Please use install.ps1 for Windows"
            ;;
        *)
            error "Unsupported operating system: $os"
            ;;
    esac
    
    case "$arch" in
        x86_64|amd64)
            ARCH="x64"
            ;;
        arm64|aarch64)
            ARCH="arm64"
            ;;
        *)
            error "Unsupported architecture: $arch"
            ;;
    esac
    
    PLATFORM="${OS}-${ARCH}"
    info "Detected platform: $PLATFORM"
}

get_latest_version() {
    info "Fetching latest version..."
    VERSION=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
    
    if [ -z "$VERSION" ]; then
        error "Failed to fetch latest version. Check your internet connection."
    fi
    
    info "Latest version: $VERSION"
}

download_binary() {
    local url="https://github.com/${REPO}/releases/download/${VERSION}/tempo-${PLATFORM}"
    local tmp_file=$(mktemp)
    
    info "Downloading from: $url"
    
    if ! curl -fsSL "$url" -o "$tmp_file"; then
        error "Failed to download binary. The release might not exist yet."
    fi
    
    # Verify download
    if [ ! -s "$tmp_file" ]; then
        error "Downloaded file is empty"
    fi
    
    echo "$tmp_file"
}

install_binary() {
    local tmp_file=$1
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Move binary
    mv "$tmp_file" "$INSTALL_DIR/$BINARY_NAME"
    chmod +x "$INSTALL_DIR/$BINARY_NAME"
    
    success "Installed to $INSTALL_DIR/$BINARY_NAME"
}

setup_path() {
    local shell_config=""
    local shell_name=$(basename "$SHELL")
    
    case "$shell_name" in
        bash)
            if [ -f "$HOME/.bashrc" ]; then
                shell_config="$HOME/.bashrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                shell_config="$HOME/.bash_profile"
            fi
            ;;
        zsh)
            shell_config="$HOME/.zshrc"
            ;;
        fish)
            shell_config="$HOME/.config/fish/config.fish"
            ;;
    esac
    
    # Check if already in PATH
    if echo "$PATH" | grep -q "$INSTALL_DIR"; then
        return
    fi
    
    if [ -n "$shell_config" ]; then
        echo "" >> "$shell_config"
        echo "# Tempo" >> "$shell_config"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$shell_config"
        warn "Added $INSTALL_DIR to PATH in $shell_config"
        warn "Run 'source $shell_config' or restart your terminal"
    else
        warn "Could not detect shell config file"
        warn "Add this to your shell config: export PATH=\"\$PATH:$INSTALL_DIR\""
    fi
}

verify_installation() {
    if [ -x "$INSTALL_DIR/$BINARY_NAME" ]; then
        success "Tempo installed successfully!"
        echo ""
        echo -e "${GREEN}To get started:${NC}"
        echo "  1. Restart your terminal (or run: source ~/.zshrc)"
        echo "  2. Run: tempo --help"
        echo ""
        echo -e "${BLUE}Example usage:${NC}"
        echo "  tempo run \"Build a REST API with authentication\""
        echo ""
    else
        error "Installation verification failed"
    fi
}

main() {
    print_banner
    detect_platform
    get_latest_version
    
    local tmp_file=$(download_binary)
    install_binary "$tmp_file"
    setup_path
    verify_installation
}

main

