"""
Phoenix Tracker - Sidecar Builder
Creates the headless sidecar executable for Tauri.
"""
import os
import sys
import subprocess
from pathlib import Path
import platform

def get_target_triple():
    """Get the target triple for the current machine."""
    # This is a simplification. Real Tauri sidecars need the exact triple.
    # Windows x64: x86_64-pc-windows-msvc
    machine = platform.machine().lower()
    if machine == 'amd64':
        return 'x86_64-pc-windows-msvc'
    else:
        return 'i686-pc-windows-msvc'

def build_sidecar():
    print("Building Sidecar Executable...")
    
    current_dir = Path(__file__).parent.absolute()
    # Source is in app/src-tauri/headless_tracker.py (but we moved it there)
    # Actually, headless_tracker.py imports stuff from root.
    # It's better to build FROM root, targeting the script.
    
    script_path = current_dir / "app" / "src-tauri" / "headless_tracker.py"
    if not script_path.exists():
        # Fallback if I didn't verify the move correctly or logic changed
        print(f"Error: Could not find {script_path}")
        return False

    # We need to include the root directory in PYTHONPATH during build
    # so PyInstaller finds the other modules (activity_detector, etc.)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(current_dir) + os.pathsep + env.get("PYTHONPATH", "")

    # Output directory: app/src-tauri/binaries/
    dist_dir = current_dir / "app" / "src-tauri" / "binaries"
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Target Filename: phoenix-tracker-x86_64-pc-windows-msvc.exe
    target_triple = get_target_triple()
    target_name = f"phoenix-tracker-{target_triple}"
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', target_name,
        '--onefile',
        '--noconfirm',
        '--distpath', str(dist_dir),
        '--specpath', str(current_dir / "build"), # temp spec folder
        '--workpath', str(current_dir / "build"),
        # Hidden imports same as before
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=win32timezone',
        '--hidden-import=pystray._win32',
        '--hidden-import=plyer.platforms.win.notification',
        '--hidden-import=mss',
        '--hidden-import=win32gui',
        '--hidden-import=websocket',
        # Paths to search
        '--paths', str(current_dir),
        str(script_path)
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, env=env, cwd=str(current_dir))
        print("✅ Sidecar built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    build_sidecar()
