"""
Setup script for Phoenix Desktop Tracker.
Helps users get started quickly.
"""
import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is sufficient."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Your version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True


def install_dependencies():
    """Install required Python packages."""
    print_header("Installing Dependencies")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        print("Installing packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def test_installation():
    """Test the installation."""
    print_header("Testing Installation")
    
    all_ok = True
    
    # Test imports
    print("Testing module imports...")
    modules = [
        'mss', 'PIL', 'cv2', 'numpy', 'psutil', 
        'requests', 'cryptography', 'pystray', 'tkinter'
    ]
    
    for module in modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'PIL':
                import PIL
            elif module == 'cv2':
                import cv2
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - not found")
            all_ok = False
    
    # Test Windows-specific modules
    if sys.platform == 'win32':
        try:
            import win32cred
            import win32con
            print(f"  ✅ pywin32")
        except ImportError:
            print(f"  ⚠️  pywin32 - not found (using fallback)")
    
    print()
    
    return all_ok


def main():
    """Main setup process."""
    print_header("Phoenix Desktop Tracker - Setup Wizard")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print()
        print("Setup failed. Please install dependencies manually:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Test installation
    if test_installation():
        print()
        print_header("Setup Complete!")
        print("✅ Phoenix Desktop Tracker is ready to use")
        print()
        print("Next steps:")
        print("  1. Run the tray application:")
        print("       start_tray.bat")
        print("  2. Configure settings by right-clicking the tray icon")
        print("  3. Set up automatic startup (see INSTALL_WINDOWS.md)")
        print()
    else:
        print()
        print("⚠️  Setup completed with warnings")
        print("Please review the errors above and fix them before running the tracker")
        print()


if __name__ == "__main__":
    main()
