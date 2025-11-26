# Phoenix Desktop Tracker - Quick Reference

## Installation (5 minutes)

```powershell
# 1. Install dependencies
python setup.py

# 2. Edit configuration
notepad .env
# Set PHOENIX_API_URL to your Phoenix server

# 3. Get device token from Phoenix Dashboard
#    Settings > Devices > Generate New Device Token

# 4. Store token securely
python token_manager.py setup
```

## Run Tracker

```powershell
# Manual start
python desktop_tracker.py

# With setup wizard
python setup.py
```

## Common Commands

```powershell
# Token management
python token_manager.py setup     # Set up authentication
python token_manager.py show      # View masked token
python token_manager.py delete    # Remove stored token

# Component testing
python window_detector.py         # Test active window detection
python activity_detector.py       # Test SSIM comparison
python gaming_detector.py         # List running processes
```

## Configuration Quick Reference

Edit `.env` file:

```env
# Required
PHOENIX_API_URL=https://your-phoenix-server.com
DEVICE_ID=workstation-1

# Performance
CAPTURE_INTERVAL=60              # Screenshot interval (seconds)
HEARTBEAT_INTERVAL=60            # Heartbeat interval (seconds)
SIMILARITY_THRESHOLD=0.95        # Change detection (0-1, higher = more similar)

# Quality
MAX_IMAGE_WIDTH=1024             # Max screenshot width
JPEG_QUALITY=70                  # JPEG compression (1-100)

# Gaming mode
GAMING_PROCESSES=steam.exe,dota2.exe,csgo.exe
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No authentication token found" | Run `python token_manager.py setup` |
| "Authentication failed" | Generate new token from Phoenix Dashboard |
| "Connection test failed" | Check `PHOENIX_API_URL` and firewall |
| Screenshots not uploading | Normal if screen hasn't changed (lower `SIMILARITY_THRESHOLD`) |
| High CPU usage | Increase `CAPTURE_INTERVAL` or reduce `MAX_IMAGE_WIDTH` |

## API Endpoints

The tracker communicates with:

- `POST /api/screentime/heartbeat` - Activity metadata (every 60s)
- `POST /api/screentime/capture` - Screenshot upload (when changed)

Headers:
```
Authorization: Bearer <DEVICE_TOKEN>
X-Device-ID: <DEVICE_ID>
```

## Auto-Start Setup (Windows)

### Quick Method - Startup Folder
```powershell
# 1. Open startup folder
Win+R > shell:startup

# 2. Create shortcut to start_tracker.bat in tracker directory
```

### Robust Method - Task Scheduler
See [INSTALL_WINDOWS.md](./INSTALL_WINDOWS.md) for detailed instructions.

## logs & Debugging

```powershell
# View logs
Get-Content phoenix_tracker.log -Tail 20

# Enable debug logging
# In .env:
LOG_LEVEL=DEBUG
```

## Security Checklist

- ✅ Using HTTPS for `PHOENIX_API_URL`
- ✅ Valid SSL certificate (or `VERIFY_SSL=true`)
- ✅ Device token stored in Windows Credential Manager
- ✅ Phoenix backend has IAM authentication
- ✅ Network restricted to trusted devices

## File Structure

```
phoenix-tracker/
├── desktop_tracker.py         # Main application ⭐
├── api_client.py              # Phoenix API client
├── token_manager.py           # Token storage
├── config.py                  # Configuration
├── window_detector.py         # Window tracking
├── activity_detector.py       # Change detection
├── gaming_detector.py         # Gaming mode
├── setup.py                   # Installation wizard
├── start_tracker.bat          # Startup script
├── requirements.txt           # Dependencies
├── .env                       # Your configuration
├── .env.example               # Template
├── README.md                  # Full documentation
└── INSTALL_WINDOWS.md         # Windows setup guide
```

## Support

1. Check [README.md](./README.md) for detailed documentation
2. Check [INSTALL_WINDOWS.md](./INSTALL_WINDOWS.md) for Windows setup
3. Review `phoenix_tracker.log` for errors
4. Test components individually (see Common Commands)

---

**Ready to start?** Run `python setup.py` and follow the prompts!
