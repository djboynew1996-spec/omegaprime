@echo off
REM ===========================================================================
REM OMEGA PRIME — Quick Start (Double-click me!)
REM ===========================================================================
REM Just double-click this file to start everything.
REM The PowerShell script handles all the heavy lifting.
REM ===========================================================================

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║     OMEGA PRIME — Quick Start            ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Starting services, please wait...
echo.

cd /d "%~dp0"

REM Launch the auto-start script
powershell.exe -ExecutionPolicy Bypass -File "start.ps1"

REM If PowerShell fails, show error
if %ERRORLEVEL% NEQ 0 (
    echo.
echo  ❌ Failed to start. Try running start.ps1 manually.
    pause
)
