@echo off
REM Phoenix Tracker - Executable Installer
REM This installs the standalone executable

echo Phoenix Tracker - Installation
echo ================================
echo.

set "INSTALL_DIR=%ProgramFiles%\PhoenixTracker"
set "EXE_PATH=%~dp0dist\PhoenixTracker.exe"

REM Check if exe exists
if not exist "%EXE_PATH%" (
    echo Error: PhoenixTracker.exe not found!
    echo Please run build_exe.py first.
    pause
    exit /b 1
)

REM Create installation directory
echo Creating installation directory...
mkdir "%INSTALL_DIR%" 2>nul

REM Copy executable
echo Installing Phoenix Tracker...
copy /Y "%EXE_PATH%" "%INSTALL_DIR%\PhoenixTracker.exe"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Installation failed. Please run as Administrator.
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo Installed to: %INSTALL_DIR%
echo.
echo To run Phoenix Tracker:
echo   1. Navigate to %INSTALL_DIR%
echo   2. Run PhoenixTracker.exe
echo.
echo To setup autostart:
echo   1. Press Win+R
echo   2. Type: shell:startup
echo   3. Create a shortcut to %INSTALL_DIR%\PhoenixTracker.exe
echo.

pause
