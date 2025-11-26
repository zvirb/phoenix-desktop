# Phoenix Desktop Screen Time Tracker - Setup Complete ✅

## Project Location
`C:\Users\marku\Documents\phoenix-desktop`

## What Was Migrated
Successfully copied from playground (`c:\Users\marku\.gemini\antigravity\playground\void-flare`):

### Core Modules (8 files)
- `desktop_tracker.py` - Main application
- `activity_detector.py` - SSIM-based screen change detection
- `api_client.py` - Phoenix API communication
- `config.py` - Configuration management
- `gaming_detector.py` - Gaming mode detection
- `token_manager.py` - Secure token storage (Windows Credential Manager)
- `window_detector.py` - Active window tracking
- `setup.py` - Setup wizard

### Documentation (3 files)
- `README.md` - Main documentation
- `INSTALL_WINDOWS.md` - Windows installation guide
- `QUICKSTART.md` - Quick start guide

### Configuration (4 files)
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template
- `.env` - Active configuration (created)
- `.gitignore` - Git ignore rules

### Scripts (2 files)
- `start_tracker.bat` - Windows startup script
- `migrate.ps1` - Migration helper script

## Environment Setup ✅
- ✅ Python 3.13.9 installed
- ✅ Virtual environment created (`venv/`)
- ✅ All dependencies installed:
  - requests 2.32.5
  - mss 10.1.0
  - pillow 12.0.0
  - psutil 7.1.3
  - opencv-python 4.12.0.88
  - numpy 2.2.6
  - pywin32 311
  - python-dotenv 1.2.1
  - cryptography 46.0.3
- ✅ Git repository initialized
- ✅ Initial commit made

## Next Steps

### 1. Configure the Tracker
Edit `.env` file with your Phoenix server details:
```bash
notepad .env
```

Required settings:
- `PHOENIX_API_URL` - Your Phoenix server URL (must use HTTPS)
- `DEVICE_ID` - Unique identifier for this device (e.g., "workstation-1")

### 2. Set Up Authentication (Optional)
If you want to store the device token securely in Windows Credential Manager:
```bash
.\venv\Scripts\activate
python token_manager.py setup
```

### 3. Test the Tracker
```bash
.\venv\Scripts\activate
python desktop_tracker.py
```

Or use the convenient batch file:
```bash
start_tracker.bat
```

### 4. Set Up Auto-Start (Optional)
See `INSTALL_WINDOWS.md` for instructions on:
- Task Scheduler setup
- Running as a background service
- Startup configuration

## Features

🔒 **Secure** - HTTPS-only, JWT authentication, Windows Credential Manager integration
📸 **Smart Screenshots** - SSIM-based change detection (only uploads when content changes)
🎮 **Gaming Mode** - Automatically pauses during gaming sessions
💓 **Heartbeat System** - Continuous activity monitoring
🪟 **Window Tracking** - Monitors active applications
⚡ **Resource Efficient** - Image compression, rate limiting, configurable intervals

## Troubleshooting

**No authentication token found:**
```bash
python token_manager.py setup
```

**Connection test failed:**
- Verify `PHOENIX_API_URL` in `.env`
- Ensure Phoenix backend is running
- Check SSL certificate validity

**High CPU usage:**
- Increase `CAPTURE_INTERVAL` in `.env` (e.g., 90 seconds)
- Reduce `MAX_IMAGE_WIDTH` (e.g., 800)
- Lower `JPEG_QUALITY` (e.g., 60)

## Documentation
- [README.md](README.md) - Full documentation
- [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) - Windows installation guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

## Support
Review logs in `phoenix_tracker.log` for detailed debugging information.
