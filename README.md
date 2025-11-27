# 🪟 Phoenix Tracker - Windows 11 System Tray Application

## ✨ New Features - Version 2.0

Phoenix Tracker has been completely redesigned as a **Windows 11 system tray application** with a modern GUI!

### What's New

✅ **System Tray Integration** - Runs silently in the background with easy access from the system tray  
✅ **Modern Windows 11 GUI** - Beautiful, clean settings interface matching Windows 11 design language  
✅ **Secure Settings Storage** - All settings stored securely in Windows Registry  
✅ **No More .env Files** - Settings managed through the GUI, stored in Windows  
✅ **Easy Token Management** - Set up authentication tokens directly from the GUI  
✅ **Start/Stop Controls** - Toggle tracking on/off from the system tray menu  
✅ **Auto-Start Ready** - Automatically starts tracking when configured  

---

## 🚀 Quick Start

### First Time Setup

1. **Run the tracker:**
   ```bash
   start_tray.bat
   ```
   
   Or:
   ```bash
   python tray_app.py
   ```

2. **Configure settings:**
   - Look for the Phoenix Tracker icon in your system tray (bottom-right of taskbar)
   - Right-click the icon → **Settings**
   - Enter your Phoenix API URL and Device ID
   - Click **Save**

3. **Setup authentication:**
   - Right-click tray icon → **Setup Token**
   - Paste your device token from Phoenix Dashboard
   - Click **OK**

4. **Start tracking:**
   - Right-click tray icon → **Start Tracking**

That's it! The tracker runs in the background and you can access it anytime from the system tray.

---

## 🎯 System Tray Features

### Menu Options

**Right-click the tray icon to access:**

- **🟢/🔴 Status** - Shows if tracker is running or stopped
- **⚙️ Settings** - Open the settings window
- **🔑 Setup Token** - Configure your authentication token
- **▶️ Start Tracking** / **⏸️ Stop Tracking** - Toggle the tracker
- **📊 View Logs** - Open the log file in your default text editor
- **📖 About** - Information about the application
- **🚪 Exit** - Close the application

### Settings Window

The modern GUI includes:

#### Server Configuration
- Phoenix API URL (with HTTPS validation)
- Device ID (auto-suggested based on computer name)

#### Capture Settings
- Capture Interval (10-3600 seconds)
- Heartbeat Interval (10-3600 seconds)
- Similarity Threshold (0-1, for change detection)

#### Performance Settings
- Max Image Width (pixels)
- JPEG Quality (1-100)

#### Security Settings
- Verify SSL Certificates (checkbox)

#### Advanced Settings
- Log Level (DEBUG, INFO, WARNING, ERROR)

#### Token Management
- View token status
- Setup new token
- Delete existing token

---

## 💾 Where Settings Are Stored

All settings are stored securely in:
- **Windows Registry:** `HKEY_CURRENT_USER\Software\PhoenixTracker`
- **Authentication Token:** Windows Credential Manager

This means:
- ✅ No plaintext configuration files
- ✅ Settings persist across updates
- ✅ Secure storage using Windows built-in security
- ✅ Per-user configuration

---

## 🔐 Security

### Token Storage
Tokens are stored in **Windows Credential Manager**, which:
- Encrypts credentials using Windows Data Protection API (DPAPI)
- Requires your Windows login to access
- Is isolated per user account
- Cannot be accessed by other users or applications without your permission

### Settings Storage
Settings in the Windows Registry are:
- Stored in your user profile (`HKEY_CURRENT_USER`)
- Protected by Windows file system permissions
- Backed up with Windows System Restore
- Easily exportable for backup

---

## 🖥️ Auto-Start on Windows Login

### Method 1: Startup Folder (Recommended)

1. Press `Win + R`
2. Type: `shell:startup`
3. Press Enter
4. Create a shortcut to `start_tray.bat` in this folder

### Method 2: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Phoenix Tracker"
4. Trigger: When I log on
5. Action: Start a program
6. Program: `C:\Users\YourName\Documents\phoenix-desktop\start_tray.bat`
7. Check "Run with highest privileges"

---

## 📁 File Structure

```
phoenix-desktop/
├── 🎯 tray_app.py              # System tray application (NEW!)
├── 🪟 windows_settings.py      # Windows Registry manager (NEW!)
├── 🖼️ gui_settings.py          # Modern settings GUI (NEW!)
├── ▶️ start_tray.bat            # Tray app launcher (NEW!)
│
├── Core Modules
│   ├── desktop_tracker.py      # Original CLI tracker (still works)
│   ├── api_client.py           # Phoenix API client
│   ├── token_manager.py        # Token storage (Windows Credential Manager)
│   ├── config.py               # Config loader (now uses Registry)
│   ├── window_detector.py      # Active window tracking
│   ├── activity_detector.py    # Screen change detection
│   └── gaming_detector.py      # Gaming mode detection
│
├── Setup & Config
│   ├── setup_wizard.py         # CLI setup wizard
│   ├── setup.py                # Dependency installer
│   └── requirements.txt        # Python dependencies
│
└── Documentation
    ├── README_TRAY.md          # This file
    ├── README.md               # Original documentation
    ├── QUICKSTART.md           # Quick reference
    └── INSTALL_WINDOWS.md      # Windows setup guide
```

---

## 🛠️ Development & Testing

### Running from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tray app
python tray_app.py

# Or use the batch file
start_tray.bat
```

### Testing GUI Components

```bash
# Test settings window
python gui_settings.py

# Test Windows Registry storage
python -c "from windows_settings import settings_manager; print(settings_manager.get_all_settings())"

# Test CLI tracker (still works)
python desktop_tracker.py
```

### Viewing Logs

- From tray menu: Right-click → View Logs
- Or open: `phoenix_tracker.log`

---

## 🔄 Migrating from Old Version

If you were using the old CLI version with `.env` file:

1. **Run the new tray app:**
   ```bash
   python tray_app.py
   ```

2. **Open Settings** from the tray menu

3. **Copy your old settings:**
   - Phoenix URL from `.env` → Settings Window
   - Device ID from `.env` → Settings Window
   - Other settings as needed

4. **Setup token:**
   - If you had a token in `.env`, set it up via "Setup Token" menu

5. **Your token is already migrated** if you used Windows Credential Manager before

The `.env` file is no longer used, but is kept for backward compatibility with the CLI mode.

---

## 🐛 Troubleshooting

### Tray icon doesn't appear
- Check if Python is running: Task Manager → Details → look for `python.exe` or `pythonw.exe`
- Check logs: `phoenix_tracker.log`
- Try running with `python tray_app.py` instead of `start_tray.bat`

### Settings not saving
- Check Windows Registry permissions
- Run as administrator if needed
- Check logs for errors

### "No settings configured" error
- Right-click tray icon → Settings
- Fill in Phoenix API URL and Device ID
- Click Save

### Tracker not starting
- Check that you have a valid token: Right-click → Setup Token
- Verify Phoenix server is accessible
- Check logs for connection errors

### High CPU usage
- Open Settings → Reduce Capture Interval
- Reduce Max Image Width
- Lower JPEG Quality

---

## 📋 System Requirements

- **OS:** Windows 10/11 (64-bit)
- **Python:** 3.8 or higher
- **RAM:** 100MB minimum
- **Disk:** 50MB for application + logs
- **Network:** HTTPS connection to Phoenix server

---

## 🎨 Customization

### Change Tray Icon

Edit `tray_app.py`, find the `create_icon_image()` function, and customize the icon design.

### Modify Menu Items

Edit `tray_app.py`, find the `create_menu()` function, and add/remove menu items.

### Add New Settings

1. Add setting to `windows_settings.py` (add getter/setter methods)
2. Add UI controls in `gui_settings.py` (add to appropriate section)
3. Use the setting in `tray_app.py` or other modules

---

## 🆘 Support

**Check These First:**
1. View Logs: Tray menu → View Logs
2. Verify Settings: Tray menu → Settings
3. Test Connection: Ensure Phoenix server is running
4. Check Token: Tray menu → Setup Token

**Still Having Issues?**
- Check `phoenix_tracker.log` for detailed error messages
- Verify Windows Registry: `regedit` → `HKEY_CURRENT_USER\Software\PhoenixTracker`
- Re-run setup: Tray menu → Settings

---

## 📝 Version History

**v2.0** - System Tray Application
- Complete redesign as Windows 11 system tray app
- Modern GUI for settings
- Windows Registry storage
- Enhanced security with Credential Manager
- Easy start/stop controls
- Auto-start support

**v1.0** - CLI Application
- Command-line desktop tracker
- .env file configuration
- Basic token management

---

## 🎉 Enjoy

Phoenix Tracker now integrates seamlessly with Windows 11, providing a clean, modern experience for tracking your desktop activity!

**Quick Tips:**
- Pin the tray icon so it's always visible
- Set up auto-start for convenience
- Adjust capture intervals to balance detail vs. performance
- Use gaming mode to automatically pause during games

Happy tracking! 🚀
