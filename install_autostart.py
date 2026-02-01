"""
Phoenix Tracker - Windows Autostart Installer
Automatically sets up Phoenix Tracker to start on Windows login.
"""
import os
import sys
import subprocess
import winshell
from pathlib import Path
from win32com.client import Dispatch


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def create_startup_shortcut():
    """Create a shortcut in Windows Startup folder."""
    try:
        print("Creating Windows Startup shortcut...")
        
        # Get the startup folder path
        startup_folder = winshell.startup()
        print(f"  Startup folder: {startup_folder}")
        
        # Get the path to start_tray.bat
        current_dir = Path(__file__).parent.absolute()
        bat_file = current_dir / "start_tray.bat"
        
        if not bat_file.exists():
            print(f"❌ Error: start_tray.bat not found at {bat_file}")
            return False
        
        # Create shortcut path
        shortcut_path = os.path.join(startup_folder, "Phoenix Tracker.lnk")
        
        # Create the shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(bat_file)
        shortcut.WorkingDirectory = str(current_dir)
        shortcut.IconLocation = str(bat_file)
        shortcut.Description = "Phoenix Desktop Tracker - Activity Monitor"
        shortcut.save()
        
        print(f"✅ Shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        return False


def create_task_scheduler_task():
    """Create a scheduled task using Task Scheduler (alternative method)."""
    try:
        print("\nCreating Task Scheduler entry as backup...")
        
        current_dir = Path(__file__).parent.absolute()
        bat_file = current_dir / "start_tray.bat"
        
        # Create the task using schtasks command
        task_name = "PhoenixTrackerTray"
        
        # First, delete existing task if it exists
        subprocess.run(
            ['schtasks', '/Delete', '/TN', task_name, '/F'],
            capture_output=True,
            shell=True
        )
        
        # Create new task
        cmd = [
            'schtasks', '/Create',
            '/TN', task_name,
            '/TR', f'"{bat_file}"',
            '/SC', 'ONLOGON',
            '/RL', 'HIGHEST',
            '/F'
        ]
        
        result = subprocess.run(cmd, capture_output=True, shell=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Task Scheduler entry created: {task_name}")
            return True
        else:
            print(f"⚠️  Task Scheduler creation warning: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️  Task Scheduler setup failed (not critical): {e}")
        return False


def remove_autostart():
    """Remove autostart configurations."""
    try:
        print_header("Removing Autostart Configuration")
        
        # Remove startup shortcut
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Phoenix Tracker.lnk")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print(f"✅ Removed startup shortcut: {shortcut_path}")
        else:
            print("  No startup shortcut found")
        
        # Remove scheduled task
        result = subprocess.run(
            ['schtasks', '/Delete', '/TN', 'PhoenixTrackerTray', '/F'],
            capture_output=True,
            shell=True
        )
        
        if result.returncode == 0:
            print("✅ Removed Task Scheduler entry")
        else:
            print("  No Task Scheduler entry found")
        
        print("\n✅ Autostart configuration removed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error removing autostart: {e}")
        return False


def verify_setup():
    """Verify that autostart is configured correctly."""
    try:
        print("\nVerifying autostart setup...")
        
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Phoenix Tracker.lnk")
        
        if os.path.exists(shortcut_path):
            print("✅ Startup shortcut exists")
            return True
        else:
            print("❌ Startup shortcut not found")
            return False
            
    except Exception as e:
        print(f"⚠️  Verification warning: {e}")
        return False


def main():
    """Main installation process."""
    print_header("Phoenix Tracker - Windows Autostart Setup")
    
    print("This tool will configure Phoenix Tracker to start automatically")
    print("when you log in to Windows.")
    print()
    
    # Check if we're on Windows
    if sys.platform != 'win32':
        print("❌ This script is only for Windows")
        sys.exit(1)
    
    # Show menu
    print("Options:")
    print("  1. Install autostart (recommended)")
    print("  2. Install autostart + Task Scheduler backup")
    print("  3. Remove autostart")
    print("  4. Verify installation")
    print("  5. Exit")
    print()
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == '1':
        print_header("Installing Autostart")
        if create_startup_shortcut():
            verify_setup()
            print()
            print("✅ Installation complete!")
            print()
            print("Phoenix Tracker will now start automatically when you log in.")
            print("You can test it by:")
            print("  1. Running the shortcut manually, or")
            print("  2. Logging out and logging back in")
            
    elif choice == '2':
        print_header("Installing Autostart with Backup")
        success = create_startup_shortcut()
        create_task_scheduler_task()
        
        if success:
            verify_setup()
            print()
            print("✅ Installation complete with backup!")
            print()
            print("Both Startup folder and Task Scheduler are configured.")
            
    elif choice == '3':
        remove_autostart()
        
    elif choice == '4':
        print_header("Verifying Installation")
        if verify_setup():
            print("\n✅ Autostart is properly configured")
        else:
            print("\n❌ Autostart is not configured")
            print("Run option 1 or 2 to set it up")
            
    elif choice == '5':
        print("Exiting...")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
