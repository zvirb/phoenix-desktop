"""
Phoenix Tracker - Executable Builder
Creates a standalone Windows executable using PyInstaller.
"""
import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PyInstaller: {e}")
        return False


def create_icon():
    """Create a simple icon file for the executable."""
    try:
        from PIL import Image, ImageDraw
        
        # Create a 256x256 icon
        img = Image.new('RGB', (256, 256), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Draw a phoenix-like symbol (simplified)
        # Orange circle in center
        draw.ellipse([78, 78, 178, 178], fill='#ff6b35', outline='#f7931e', width=4)
        
        # Inner circle
        draw.ellipse([98, 98, 158, 158], fill='#ffd700', outline='#ff8c00', width=2)
        
        # Save as ICO
        icon_path = Path(__file__).parent / "phoenix_icon.ico"
        img.save(str(icon_path), format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        
        print(f"✅ Icon created: {icon_path}")
        return str(icon_path)
        
    except Exception as e:
        print(f"⚠️  Could not create icon: {e}")
        return None


def build_executable():
    """Build the executable using PyInstaller."""
    print_header("Building Phoenix Tracker Executable")
    
    current_dir = Path(__file__).parent.absolute()
    
    # Create icon
    icon_path = create_icon()
    
    # Find site-packages directory for explicit data inclusion
    import site
    site_packages = site.getsitepackages()[0] if site.getsitepackages() else ""
    if not site_packages or "venv" not in site_packages:
        # Fallback to a common venv path if site.getsitepackages() is unfriendly
        site_packages = str(current_dir / "venv" / "Lib" / "site-packages")

    # PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=PhoenixTracker',
        '--onefile',  # Single executable file
        '--windowed',  # No console window (GUI app)
        '--noconfirm',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=win32timezone',
        '--hidden-import=pystray._win32',
        '--hidden-import=plyer.platforms.win.notification',
        '--hidden-import=customtkinter',
        '--hidden-import=darkdetect',
        '--collect-all=customtkinter',
        '--collect-all=plyer',
        '--collect-all=pystray',
        f'--add-data={current_dir}/gui;gui',  # Include gui package
        f'--add-data={current_dir}/phoenix;phoenix',  # Include phoenix package (for assets/ui)
    ]

    # Explicitly add package data to avoid "ModuleNotFoundError" or missing themes
    for pkg in ['customtkinter', 'plyer', 'pystray']:
        pkg_path = f"{site_packages}/{pkg}"
        if os.path.exists(pkg_path):
            cmd.append(f'--add-data={pkg_path};{pkg}')
    
    # Add icon if created
    if icon_path:
        cmd.extend(['--icon', icon_path])
    
    # Add the main script
    cmd.append('tray_app.py')
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.check_call(cmd, cwd=str(current_dir))
        
        exe_path = current_dir / 'dist' / 'PhoenixTracker.exe'
        
        if exe_path.exists():
            print()
            print_header("Build Successful!")
            print(f"✅ Executable created: {exe_path}")
            print()
            print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            print()
            print("Next steps:")
            print(f"  1. Test the executable by running: {exe_path}")
            print(f"  2. Move it to a permanent location (e.g., C:\\Program Files\\PhoenixTracker\\)")
            print(f"  3. Create a startup shortcut pointing to the .exe instead of .bat")
            print()
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False


def create_installer_script():
    """Create a simple batch installer for the executable."""
    installer_content = """@echo off
REM Phoenix Tracker - Executable Installer
REM This installs the standalone executable

echo Phoenix Tracker - Installation
echo ================================
echo.

set "INSTALL_DIR=%ProgramFiles%\\PhoenixTracker"
set "EXE_PATH=%~dp0dist\\PhoenixTracker.exe"

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
copy /Y "%EXE_PATH%" "%INSTALL_DIR%\\PhoenixTracker.exe"

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
echo   3. Create a shortcut to %INSTALL_DIR%\\PhoenixTracker.exe
echo.

pause
"""
    
    installer_path = Path(__file__).parent / "install_exe.bat"
    installer_path.write_text(installer_content)
    print(f"✅ Installer script created: {installer_path}")


def main():
    """Main build process."""
    print_header("Phoenix Tracker - Executable Builder")
    
    print("This tool creates a standalone Windows executable (.exe) that doesn't")
    print("require Python to be installed on the target machine.")
    print()
    print("Note: The executable will be larger (~50-100MB) but is easier to distribute.")
    print()
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller is not installed. Installing...")
        if not install_pyinstaller():
            sys.exit(1)
    else:
        print("✅ PyInstaller is installed")
    
    print("Starting build process...")
    if build_executable():
        create_installer_script()
        print()
        print("✅ All done!")
    else:
        print("❌ Build failed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
