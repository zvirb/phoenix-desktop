@echo off
REM Phoenix Tracker - System Tray Launcher
REM This script starts the Phoenix Tracker in system tray mode

echo Starting Phoenix Tracker (System Tray)...

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the system tray app (hidden window mode)
pythonw tray_app.py

REM If pythonw doesn't work, fall back to python
if %ERRORLEVEL% NEQ 0 (
    python tray_app.py
)
