"""
Quick verification script to check if Phoenix Tracker autostart is configured.
"""
import os
import winshell
from pathlib import Path


def main():
    print()
    print("=" * 70)
    print("  Phoenix Tracker - Autostart Verification")
    print("=" * 70)
    print()
    
    all_good = True
    
    # Check startup shortcut
    startup_folder = winshell.startup()
    shortcut_path = os.path.join(startup_folder, "Phoenix Tracker.lnk")
    
    print("1. Checking Startup Folder...")
    print(f"   Location: {startup_folder}")
    
    if os.path.exists(shortcut_path):
        print(f"   ✅ Shortcut exists: Phoenix Tracker.lnk")
    else:
        print(f"   ❌ Shortcut NOT found")
        all_good = False
    
    # Check if start_tray.bat exists
    print()
    print("2. Checking Application Files...")
    current_dir = Path(__file__).parent.absolute()
    bat_file = current_dir / "start_tray.bat"
    tray_app = current_dir / "tray_app.py"
    
    if bat_file.exists():
        print(f"   ✅ start_tray.bat exists")
    else:
        print(f"   ❌ start_tray.bat NOT found")
        all_good = False
    
    if tray_app.exists():
        print(f"   ✅ tray_app.py exists")
    else:
        print(f"   ❌ tray_app.py NOT found")
        all_good = False
    
    # Summary
    print()
    print("=" * 70)
    if all_good:
        print("  ✅ VERIFICATION PASSED")
        print()
        print("  Phoenix Tracker is configured to start automatically!")
        print()
        print("  Test it:")
        print("    • Log out and log back in")
        print("    • OR restart your computer")
        print("    • Look for the Phoenix icon in your system tray")
    else:
        print("  ❌ VERIFICATION FAILED")
        print()
        print("  Some components are missing. Please run:")
        print("    python install_autostart.py")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
