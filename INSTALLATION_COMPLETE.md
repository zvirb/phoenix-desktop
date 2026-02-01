# ✅ Phoenix Tracker - Autostart Installation Complete!

## What Was Done

Your Phoenix Tracker application has been successfully configured to **start automatically on Windows startup**!

### Installation Summary

✅ **Startup Shortcut Created**
- Location: `C:\Users\marku\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Phoenix Tracker.lnk`
- Points to: `start_tray.bat` in your phoenix-desktop folder
- Status: **Active**

⚠️ **Task Scheduler** (Optional Backup)
- Status: Requires Administrator privileges
- Not critical - the startup shortcut is sufficient

---

## How It Works

When you log in to Windows:

1. Windows automatically runs shortcuts in the Startup folder
2. `Phoenix Tracker.lnk` shortcut executes `start_tray.bat`
3. The batch file:
   - Activates your virtual environment (if present)
   - Runs `pythonw tray_app.py` (hidden window mode)
4. Phoenix Tracker appears in your **system tray** (bottom-right corner)

---

## Testing

### Test it now (without restarting):

```bash
start_tray.bat
```

Look for the Phoenix icon in your system tray!

### Test the autostart:

1. **Log out** and **log back in**, OR
2. **Restart** your computer
3. Check the system tray for the Phoenix icon

> **Note:** If you don't see the icon, click the `^` arrow in the system tray to reveal hidden icons.

---

## Files Created

The following new files were added to your project:

| File | Purpose |
|------|---------|
| `install_autostart.py` | Automated installer for Windows autostart |
| `verify_autostart.py` | Verification script to check setup |
| `build_exe.py` | Optional: Build standalone .exe |
| `AUTOSTART_GUIDE.md` | Comprehensive setup guide |
| `install_autostart_option2.bat` | Quick installer (auto-selects option 2) |

---

## Quick Commands

### Verify Installation
```bash
python verify_autostart.py
```

### Reinstall/Reconfigure
```bash
python install_autostart.py
```

### Remove Autostart
```bash
python install_autostart.py
# Then select option 3
```

### Build Standalone Executable (Optional)
```bash
python build_exe.py
```

---

## What's Next?

### Optional Steps

1. **Add Task Scheduler Backup (Requires Admin)**
   - Right-click Command Prompt → "Run as administrator"
   - Run: `python install_autostart.py`
   - Select option 2
   - This adds redundancy in case the startup shortcut fails

2. **Build Standalone Executable**
   - Run: `python build_exe.py`
   - Creates a single .exe file that doesn't require Python
   - Useful for distribution or cleaner installation

3. **Pin to Taskbar**
   - When the app is running, right-click the tray icon
   - Select "Pin to taskbar" (if available)
   - Or keep it visible in the system tray

### Recommended Settings

Open the Phoenix Tracker settings (right-click tray icon → Settings) and configure:

- ✅ Device token
- ✅ API endpoint
- ✅ Tracking intervals
- ✅ Screenshot settings

---

## Troubleshooting

### Icon doesn't appear after login

1. **Check if it's hidden:**
   - Click the `^` arrow in the system tray
   - Look for the Phoenix icon there

2. **Check if Python is running:**
   - Open Task Manager (`Ctrl+Shift+Esc`)
   - Look for `pythonw.exe` process

3. **Check the logs:**
   ```bash
   type phoenix_tracker.log
   ```

4. **Test manually:**
   ```bash
   start_tray.bat
   ```

### "Python not found" error

- Make sure Python is in your PATH
- Or update `start_tray.bat` to use full Python path:
  ```batch
  "C:\Users\marku\AppData\Local\Programs\Python\Python313\pythonw.exe" tray_app.py
  ```

### App starts but crashes immediately

1. Check the log: `phoenix_tracker.log`
2. Verify all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Test the app manually:
   ```bash
   python tray_app.py
   ```

---

## Uninstallation

To remove the autostart feature:

### Quick Method
```bash
python install_autostart.py
# Select option 3 (Remove autostart)
```

### Manual Method
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Delete `Phoenix Tracker.lnk`

---

## Documentation

For more detailed information, see:

- **[AUTOSTART_GUIDE.md](./AUTOSTART_GUIDE.md)** - Comprehensive setup guide
- **[INSTALL_WINDOWS.md](./INSTALL_WINDOWS.md)** - Original installation guide
- **[README.md](./README.md)** - Project overview

---

## Summary

✅ **Autostart is configured and ready!**

Your Phoenix Tracker will now start automatically every time you log in to Windows. The app runs silently in the background and appears only as an icon in your system tray.

**To verify:** Log out and log back in, then check your system tray for the Phoenix icon.

---

*Last updated: December 3, 2025*
*Installation method: Startup Folder (Option 2)*
