# Tempo Installer for Windows PowerShell
# Usage: irm https://raw.githubusercontent.com/YOUR_USERNAME/tempo/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

# Configuration
$Repo = "tomalmog/tempo"
$InstallDir = "$env:LOCALAPPDATA\Tempo"
$BinaryName = "tempo.exe"
$TrackingUrl = "https://tempo-eight-zeta.vercel.app/api/downloads/track?url=cli-install"

function Write-Banner {
    Write-Host ""
    Write-Host "  ╔════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "  ║           Tempo Installer              ║" -ForegroundColor Blue
    Write-Host "  ║   Automated Claude Code Runner         ║" -ForegroundColor Blue
    Write-Host "  ╚════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "INFO: " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "SUCCESS: " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warn {
    param([string]$Message)
    Write-Host "WARNING: " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "ERROR: " -ForegroundColor Red -NoNewline
    Write-Host $Message
    exit 1
}

function Get-LatestVersion {
    Write-Info "Fetching latest version..."
    
    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
        $version = $release.tag_name
        Write-Info "Latest version: $version"
        return $version
    }
    catch {
        Write-Error "Failed to fetch latest version. Check your internet connection."
    }
}

function Get-Binary {
    param([string]$Version)
    
    $url = "https://github.com/$Repo/releases/download/$Version/tempo-windows-x64.exe"
    $tempFile = [System.IO.Path]::GetTempFileName() + ".exe"
    
    Write-Info "Downloading from: $url"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $tempFile -UseBasicParsing
    }
    catch {
        Write-Error "Failed to download binary. The release might not exist yet."
    }
    
    if (-not (Test-Path $tempFile) -or (Get-Item $tempFile).Length -eq 0) {
        Write-Error "Downloaded file is empty or missing"
    }
    
    return $tempFile
}

function Install-Binary {
    param([string]$TempFile)
    
    # Create install directory
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
    
    # Move binary
    $targetPath = Join-Path $InstallDir $BinaryName
    Move-Item -Path $TempFile -Destination $targetPath -Force
    
    Write-Success "Installed to $targetPath"
}

function Add-ToPath {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($currentPath -like "*$InstallDir*") {
        Write-Info "Already in PATH"
        return
    }
    
    $newPath = "$currentPath;$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    
    # Update current session
    $env:Path = "$env:Path;$InstallDir"
    
    Write-Success "Added $InstallDir to PATH"
}

function Track-Download {
    # Silently ping the tracking API (don't fail if it doesn't work)
    try {
        Invoke-WebRequest -Uri $TrackingUrl -UseBasicParsing -TimeoutSec 5 | Out-Null
    }
    catch {
        # Ignore tracking errors
    }
}

function Test-Installation {
    $binaryPath = Join-Path $InstallDir $BinaryName
    
    if (Test-Path $binaryPath) {
        # Track successful installation
        Track-Download
        
        Write-Success "Tempo installed successfully!"
        Write-Host ""
        Write-Host "To get started:" -ForegroundColor Green
        Write-Host "  1. Restart your terminal (or open a new one)"
        Write-Host "  2. Run: tempo --help"
        Write-Host ""
        Write-Host "Example usage:" -ForegroundColor Blue
        Write-Host "  tempo run `"Build a REST API with authentication`""
        Write-Host ""
    }
    else {
        Write-Error "Installation verification failed"
    }
}

function Main {
    Write-Banner
    
    $version = Get-LatestVersion
    $tempFile = Get-Binary -Version $version
    Install-Binary -TempFile $tempFile
    Add-ToPath
    Test-Installation
}

Main

