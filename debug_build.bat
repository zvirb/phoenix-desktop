@echo off
SET VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community
SET CARGO_PATH=C:\Users\marku\.cargo\bin

echo Setting up Visual Studio Environment...
call "%VS_PATH%\Common7\Tools\VsDevCmd.bat"
if %errorlevel% neq 0 (
    echo Error: Failed to setup VS environment
    exit /b %errorlevel%
)

echo Adding Cargo to PATH...
set PATH=%PATH%;%CARGO_PATH%

echo Checking Linker...
link.exe /VERSION
if %errorlevel% neq 0 (
    echo Error: Linker not found or failed
)

echo Building Rust Backend...
cd app\src-tauri
cargo build --verbose
