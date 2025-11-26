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


def create_env_file():
    """Create .env file from template."""
    print_header("Creating Configuration File")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping configuration file creation")
            return True
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    # Copy template
    env_file.write_text(env_example.read_text())
    
    print("✅ Created .env file")
    print()
    print("⚠️  IMPORTANT: Edit .env and set your Phoenix server URL:")
    print(f"   {env_file.absolute()}")
    print()
    
    # Ask if user wants to edit now
    response = input("Open .env for editing now? (Y/n): ")
    if response.lower() != 'n':
        try:
            if sys.platform == 'win32':
                os.startfile(env_file)
            else:
                subprocess.call(['xdg-open', env_file])
        except Exception:
            print(f"Please edit manually: {env_file}")
    
    return True


def setup_token():
    """Run token setup wizard."""
    print_header("Authentication Setup")
    
    print("To use the tracker, you need a device token from Phoenix.")
    print()
    response = input("Set up authentication token now? (Y/n): ")
    
    if response.lower() == 'n':
        print("Skipping token setup. Run later with:")
        print("  python token_manager.py setup")
        return True
    
    try:
        from token_manager import TokenManager
        manager = TokenManager()
        return manager.setup_wizard()
    except Exception as e:
        print(f"❌ Token setup failed: {e}")
        return False


def test_installation():
    """Test the installation."""
    print_header("Testing Installation")
    
    all_ok = True
    
    # Test imports
    print("Testing module imports...")
    modules = [
        'mss', 'PIL', 'cv2', 'numpy', 'psutil', 
        'requests', 'dotenv', 'cryptography'
    ]
    
    for module in modules:
        try:
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
    
    # Test configuration
    try:
        from config import config
        config.validate()
        print("✅ Configuration valid")
    except Exception as e:
        print(f"⚠️  Configuration issue: {e}")
        print("   Please update your .env file")
        all_ok = False
    
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
    
    # Create .env file
    if not create_env_file():
        print("Please create .env file manually from .env.example")
    
    # Set up authentication
    setup_token()
    
    # Test installation
    if test_installation():
        print()
        print_header("Setup Complete!")
        print("✅ Phoenix Desktop Tracker is ready to use")
        print()
        print("Next steps:")
        print("  1. Verify your .env configuration")
        print("  2. Run the tracker:")
        print("       python desktop_tracker.py")
        print("  3. Set up automatic startup (see INSTALL_WINDOWS.md)")
        print()
    else:
        print()
        print("⚠️  Setup completed with warnings")
        print("Please review the errors above and fix them before running the tracker")
        print()


if __name__ == "__main__":
    main()
