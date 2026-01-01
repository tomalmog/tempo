@echo off
REM Tempo Installer for Windows CMD
REM Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/tempo/main/install.cmd -o install.cmd && install.cmd

echo.
echo   ========================================
echo            Tempo Installer
echo      Automated Claude Code Runner
echo   ========================================
echo.

REM Configuration
set REPO=tomalmog/tempo
set INSTALL_DIR=%LOCALAPPDATA%\Tempo
set BINARY_NAME=tempo.exe

REM Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Get latest version
echo Fetching latest version...
for /f "tokens=*" %%i in ('powershell -Command "(Invoke-RestMethod -Uri 'https://api.github.com/repos/%REPO%/releases/latest').tag_name"') do set VERSION=%%i
echo Latest version: %VERSION%

REM Download binary
set URL=https://github.com/%REPO%/releases/download/%VERSION%/tempo-windows-x64.exe
echo Downloading from: %URL%
powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%INSTALL_DIR%\%BINARY_NAME%'"

REM Add to PATH
echo Adding to PATH...
setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1

echo.
echo SUCCESS: Tempo installed to %INSTALL_DIR%\%BINARY_NAME%
echo.
echo To get started:
echo   1. Open a new command prompt
echo   2. Run: tempo --help
echo.

pause

