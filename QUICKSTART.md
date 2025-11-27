# Phoenix Desktop Tracker - Quick Reference

## Installation (5 minutes)

```powershell
# 1. Install dependencies
python setup.py

# 2. Run the tray app
start_tray.bat
# Or: python tray_app.py

# 3. Configure settings
#    Right-click tray icon > Settings
#    Enter Phoenix API URL and Device ID

# 4. Setup authentication
#    Right-click tray icon > Setup Token
#    Paste token from Phoenix Dashboard
```

## Common Commands

```powershell
# Start the tracker (System Tray)
start_tray.bat

# Run manually (if bat fails)
python tray_app.py

# Token management (CLI alternative)
python token_manager.py setup     # Set up authentication
python token_manager.py show      # View masked token
python token_manager.py delete    # Remove stored token
```

## Configuration

All configuration is managed via the **Settings** window in the system tray application.
Settings are stored securely in the Windows Registry.

### Key Settings
- **Phoenix API URL**: Your Phoenix server address (HTTPS)
- **Device ID**: Unique identifier for this computer
- **Capture Interval**: How often to check for screen changes (seconds)
- **Gaming Mode**: Automatically pauses when games are detected

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tray icon doesn't appear | Check if `python.exe` is running in Task Manager |
| "No settings configured" | Open Settings from tray menu and save configuration |
| "No authentication token" | Use "Setup Token" from tray menu |
| Screenshots not uploading | Normal if screen hasn't changed (lower Similarity Threshold) |

## Auto-Start Setup

See [INSTALL_WINDOWS.md](./INSTALL_WINDOWS.md) for instructions on adding `start_tray.bat` to your Startup folder.

## Support

1. Right-click tray icon > **View Logs**
2. Check `phoenix_tracker.log`
3. Verify settings in the GUI

---

**Ready to start?** Run `start_tray.bat`!
