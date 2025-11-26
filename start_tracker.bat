@echo off
REM Startup script for Phoenix Desktop Tracker
REM Place this in your Windows Startup folder or use with Task Scheduler

echo Starting Phoenix Desktop Tracker...
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the tracker
python desktop_tracker.py

REM If the script exits unexpectedly, pause to see the error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Tracker exited with error code %ERRORLEVEL%
    pause
)
