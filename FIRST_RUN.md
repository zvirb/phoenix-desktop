# Phoenix Desktop Tracker - First Run Guide

## 🎉 Quick Start (2 Minutes)

### Step 1: Run the Tracker

Simply run:
```bash
python desktop_tracker.py
```

or

```bash
start_tracker.bat
```

### Step 2: Complete the Setup Wizard

On first run, you'll see an **automatic setup wizard** that will ask you:

1. **Phoenix Server URL**
   - Your Phoenix server address (must be HTTPS)
   - Example: `https://phoenix.example.com`
   - Example: `https://192.168.1.100:8000`
   - Example: `https://localhost:8000` (for testing)

2. **Device ID**
   - A unique identifier for this computer
   - Default suggestion: `desktop-<your-computer-name>`
   - You can use any unique name: `work-laptop`, `home-pc`, etc.

The wizard will automatically save your settings to the `.env` file.

### Step 3: Set Up Authentication (Optional)

After the initial setup, you can optionally store your device token securely:

```bash
python token_manager.py setup
```

This stores the token in Windows Credential Manager for added security.

---

## Manual Setup (Alternative)

If you prefer to configure manually:

1. **Edit the `.env` file:**
   ```bash
   notepad .env
   ```

2. **Set these required values:**
   ```env
   PHOENIX_API_URL=https://your-phoenix-server.com
   DEVICE_ID=your-device-name
   ```

3. **Run the tracker:**
   ```bash
   python desktop_tracker.py
   ```

---

## Setup Wizard Features

The wizard automatically:
- ✅ Validates your Phoenix server URL
- ✅ Ensures HTTPS is used for security
- ✅ Suggests a unique device ID based on your computer name
- ✅ Saves configuration to `.env` file
- ✅ Provides clear next steps

### Re-running the Setup Wizard

You can manually run the setup wizard anytime:
```bash
python setup_wizard.py
```

This will update your configuration without affecting other settings.

---

## What Happens Next?

After setup completes, the tracker will:

1. **Initialize** - Connect to your Phoenix server
2. **Authenticate** - Verify your device token
3. **Start Tracking** - Begin capturing screen activity

You'll see output like:
```
✅ Tracker initialized successfully
Capture interval: 60s
Heartbeat interval: 60s
Press Ctrl+C to stop
```

---

## Troubleshooting First Run

### "PHOENIX_API_URL must use HTTPS protocol"
- The wizard will automatically add `https://` if you forget it
- For local testing, HTTPS is still recommended but `http://localhost` is allowed

### "No authentication token found"
- This is normal on first run
- Generate a device token from your Phoenix Dashboard
- Run: `python token_manager.py setup`

### "Connection test failed"
- Verify your Phoenix server is running
- Check that the URL is correct
- Ensure firewall allows HTTPS connections
- Try accessing the URL in your web browser

### Wizard doesn't appear
- The wizard only runs if `.env` contains placeholder values
- To force it to run: `python setup_wizard.py`
- Or manually edit `.env` and run the tracker again

---

## Configuration Reference

After setup, your `.env` file will contain:

```env
# Required (set by wizard)
PHOENIX_API_URL=https://your-server.com
DEVICE_ID=desktop-hostname

# Optional (can customize later)
CAPTURE_INTERVAL=60              # Screenshot interval in seconds
HEARTBEAT_INTERVAL=60            # Heartbeat interval in seconds
SIMILARITY_THRESHOLD=0.95        # Change detection sensitivity (0-1)
MAX_IMAGE_WIDTH=1024             # Max screenshot width in pixels
JPEG_QUALITY=70                  # JPEG compression quality (1-100)
VERIFY_SSL=true                  # Verify SSL certificates
LOG_LEVEL=INFO                   # Logging level (DEBUG, INFO, WARNING, ERROR)
```

To customize these settings, edit the `.env` file anytime.

---

## Next Steps After Setup

1. **Generate Device Token** (if you haven't already)
   - Log into Phoenix Web Dashboard
   - Go to Settings → Devices
   - Click "Generate New Device Token"
   - Copy the token
   - Run: `python token_manager.py setup`

2. **Configure Auto-Start** (optional)
   - See `INSTALL_WINDOWS.md` for detailed instructions
   - Quick method: Add `start_tracker.bat` to Windows Startup folder

3. **Monitor Activity**
   - View logs: `phoenix_tracker.log`
   - Check Phoenix Dashboard for captured data

---

## Getting Help

- 📖 Full documentation: `README.md`
- 🪟 Windows setup guide: `INSTALL_WINDOWS.md`
- ⚡ Quick reference: `QUICKSTART.md`
- 📋 Setup complete guide: `SETUP_COMPLETE.md`

For issues, check `phoenix_tracker.log` for detailed error messages.
