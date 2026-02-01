@echo off
REM Quick test launcher for Phoenix Tracker
echo.
echo ========================================
echo   Testing Phoenix Tracker
echo ========================================
echo.
echo Starting Phoenix Tracker in test mode...
echo Look for the icon in your system tray!
echo.
echo Press Ctrl+C in this window to stop the app.
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
)

REM Run with visible console for testing
python tray_app.py

echo.
echo App stopped.
pause
