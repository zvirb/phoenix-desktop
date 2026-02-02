@echo off
REM Phoenix Companion Dev Launcher
REM Sets up Visual Studio environment variables and runs Tauri

SET VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community
SET CARGO_PATH=C:\Users\marku\.cargo\bin

echo Setting up Visual Studio Environment...
call "%VS_PATH%\Common7\Tools\VsDevCmd.bat"

echo Adding Cargo to PATH...
set PATH=%PATH%;%CARGO_PATH%

echo Starting Tauri Dev Server...
cd app
npm run tauri dev
