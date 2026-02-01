# Phoenix Tracker - Windows Autostart Setup Guide

This guide provides **three methods** to set up Phoenix Tracker to start automatically on Windows. Choose the one that best fits your needs.

---

## 🚀 Quick Start (Recommended)

**Use the automated installer:**

```bash
python install_autostart.py
```

Then select **option 2** for the most reliable setup (Startup Folder + Task Scheduler backup).

---

## Method 1: Automated Installation (Easiest) ⭐

### Prerequisites
- Python 3.8+ installed
- Virtual environment activated (if you're using one)

### Steps

1. **Install required dependency:**
   ```bash
   pip install winshell
   ```

2. **Run the installer:**
   ```bash
   python install_autostart.py
   ```

3. **Select option 2** (Install autostart + Task Scheduler backup)

4. **Verify:** Log out and log back in, or restart your computer. The Phoenix Tracker icon should appear in your system tray automatically.

### What This Does
- Creates a shortcut in your Windows Startup folder (`shell:startup`)
- Creates a backup Task Scheduler entry
- Configures the app to run with highest privileges
- Sets it to start on every login

---

## Method 2: Build Standalone Executable (No Python Required)

If you want to **distribute** Phoenix Tracker or **run it without Python installed**, create a standalone executable.

### Steps

1. **Build the executable:**
   ```bash
   python build_exe.py
   ```
   
   This creates `dist/PhoenixTracker.exe` (~50-100MB)

2. **Install the executable (optional):**
   ```bash
   install_exe.bat
   ```
   
   This installs to `C:\Program Files\PhoenixTracker\`

3. **Setup autostart manually:**
   - Press `Win + R`
   - Type `shell:startup` and press Enter
   - Right-click in the folder → New → Shortcut
   - Point to `C:\Program Files\PhoenixTracker\PhoenixTracker.exe`
   - Name it "Phoenix Tracker"

### Advantages
- ✅ No Python installation required
- ✅ Easy to distribute to other computers
- ✅ Cleaner, more professional deployment

### Disadvantages
- ❌ Larger file size (~50-100MB vs ~500KB)
- ❌ Slower startup time
- ❌ Requires rebuilding for updates

---

## Method 3: Manual Setup (No Scripts)

If you prefer to set things up manually:

### Option A: Startup Folder (Simplest)

1. **Open Startup folder:**
   - Press `Win + R`
   - Type `shell:startup`
   - Press Enter

2. **Create shortcut:**
   - Navigate to your `phoenix-desktop` folder
   - Right-click on `start_tray.bat`
   - Select "Create shortcut"
   - Move the shortcut to the Startup folder

3. **Test:**
   - Log out and log back in
   - Check system tray for Phoenix icon

### Option B: Task Scheduler (More Control)

1. **Open Task Scheduler:**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create task:**
   - Click "Create Basic Task..."
   - **Name:** `Phoenix Tracker Tray`
   - **Trigger:** "When I log on"
   - **Action:** "Start a program"
   - **Program/script:** Browse to `start_tray.bat`

3. **Configure:**
   - Right-click the task → Properties
   - **General tab:** Check "Run with highest privileges"
   - **Conditions tab:** Uncheck "Start only if on AC power" (laptops)
   - Click OK

---

## 🔍 Verification

### Check if autostart is working:

1. **Verify startup shortcut exists:**
   - Press `Win + R`
   - Type `shell:startup`
   - Look for "Phoenix Tracker.lnk"

2. **Verify Task Scheduler entry:**
   - Open Task Scheduler (`taskschd.msc`)
   - Look for "PhoenixTrackerTray" task

3. **Test the setup:**
   ```bash
   python install_autostart.py
   ```
   Select **option 4** (Verify installation)

---

## 🛠️ Troubleshooting

### App doesn't start on login

**Check if Python is in PATH:**
```bash
python --version
```

**Check if virtual environment is activated:**
- The `start_tray.bat` script should handle this automatically

**Check logs:**
```
phoenix_tracker.log
```

**Manually test the batch file:**
```bash
start_tray.bat
```

### Icon doesn't appear in system tray

- Windows often hides tray icons by default
- Click the `^` arrow in the system tray
- Drag the Phoenix icon to the taskbar to keep it visible
- **Or** go to Settings → Personalization → Taskbar → Other system tray icons

### "Access Denied" errors

- Run `install_autostart.py` as Administrator:
  - Right-click Command Prompt
  - Select "Run as administrator"
  - Navigate to the folder and run the script

### Task Scheduler task doesn't run

- Open Task Scheduler
- Find "PhoenixTrackerTray"
- Right-click → Run
- Check the "Last Run Result" column
- If it shows an error code, check the History tab

---

## 🗑️ Uninstallation

### Remove autostart:

**Option 1: Use the installer**
```bash
python install_autostart.py
```
Select **option 3** (Remove autostart)

**Option 2: Manual removal**

1. **Remove startup shortcut:**
   - Press `Win + R` → `shell:startup`
   - Delete "Phoenix Tracker.lnk"

2. **Remove Task Scheduler entry:**
   - Open Task Scheduler (`taskschd.msc`)
   - Delete "PhoenixTrackerTray" task

3. **Stop the running app:**
   - Right-click tray icon → Exit

4. **Delete stored credentials (optional):**
   ```bash
   python token_manager.py delete
   ```

5. **Remove files:**
   - Delete the `phoenix-desktop` folder

---

## 📋 Comparison of Methods

| Method | Ease | Python Required | File Size | Best For |
|--------|------|-----------------|-----------|----------|
| **Automated (Option 2)** | ⭐⭐⭐ | ✅ Yes | Small | Development & personal use |
| **Executable** | ⭐⭐ | ❌ No | Large (~50MB) | Distribution & production |
| **Manual** | ⭐ | ✅ Yes | Small | Learning & customization |

---

## 🎯 Recommended Setup

For **most users**, we recommend:

1. Run `python install_autostart.py`
2. Select option **2** (Startup + Task Scheduler)
3. Verify with option **4**

This provides:
- ✅ Automatic startup on login
- ✅ Redundancy (two methods)
- ✅ Easy removal if needed
- ✅ No manual configuration required

---

## 📝 Advanced Configuration

### Running as a Windows Service

For advanced users who want Phoenix Tracker to run as a background service (even before login), you can use tools like:
- [NSSM (Non-Sucking Service Manager)](https://nssm.cc/)
- Windows Service Wrapper

This is typically **not necessary** for a user-level tracker application.

### Docker/Container Support

Phoenix Tracker requires access to:
- Windows GUI APIs (system tray)
- Screen capture
- Window detection

Therefore, **containerization is not recommended** for this application as it needs direct access to the Windows desktop environment.

---

## ❓ FAQ

**Q: Will this slow down my computer startup?**  
A: No. The app starts in the background and uses minimal resources (~50MB RAM, <1% CPU when idle).

**Q: Can I run multiple instances?**  
A: Not recommended. The app maintains a single configuration and database.

**Q: Does it work on Windows 11?**  
A: Yes, fully tested on Windows 10 and Windows 11.

**Q: Can I change when the app starts?**  
A: Yes. Modify the Task Scheduler trigger or move the startup shortcut to a different folder.

**Q: Will it survive Windows updates?**  
A: Yes. The startup configuration persists through Windows updates.

---

## 🆘 Support

If you encounter issues:

1. Check the logs: `phoenix_tracker.log`
2. Verify installation: Run `python install_autostart.py` → option 4
3. Test manually: Run `start_tray.bat`
4. Check the [troubleshooting section](#-troubleshooting) above

---

**Last updated:** December 2025
