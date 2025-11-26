# ✅ Phoenix Desktop Tracker - Ready to Use!

## 🎉 What's New

I've added an **automatic setup wizard** that runs on first launch! No more manual `.env` editing required.

## 🚀 How to Run

### First Time Setup (Automatic)

Simply run:
```bash
python desktop_tracker.py
```

The app will automatically detect it's the first run and launch an interactive setup wizard that will ask you for:

1. **Phoenix Server URL** - Your Phoenix server address (e.g., `https://phoenix.example.com`)
2. **Device ID** - A unique identifier for this computer (e.g., `desktop-MYCOMPUTER`)

The wizard will:
- ✅ Validate your inputs
- ✅ Ensure HTTPS is used
- ✅ Suggest a default device ID based on your computer name
- ✅ Save everything to `.env` automatically
- ✅ Start the tracker immediately after setup

### Manual Setup (Alternative)

You can also run the wizard separately:
```bash
python setup_wizard.py
```

Or edit `.env` manually:
```bash
notepad .env
```

---

## 📁 Project Structure

```
phoenix-desktop/
├── 🎯 desktop_tracker.py        # Main app (auto-runs wizard on first start)
├── 🧙 setup_wizard.py            # Interactive configuration wizard (NEW!)
├── 📘 FIRST_RUN.md               # First-time user guide (NEW!)
├── ✅ SETUP_COMPLETE.md          # Setup completion summary (NEW!)
│
├── Core Modules
│   ├── api_client.py             # Phoenix API client
│   ├── token_manager.py          # Secure token storage
│   ├── config.py                 # Configuration loader
│   ├── window_detector.py        # Active window tracking
│   ├── activity_detector.py      # Screen change detection (SSIM)
│   └── gaming_detector.py        # Gaming mode detection
│
├── Documentation
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # Quick reference
│   └── INSTALL_WINDOWS.md        # Windows setup guide
│
├── Configuration
│   ├── .env                      # Your settings (created by wizard)
│   ├── .env.example              # Template
│   ├── requirements.txt          # Python dependencies
│   └── .gitignore                # Git ignore rules
│
└── Scripts
    ├── setup.py                  # Dependency installer
    ├── start_tracker.bat         # Quick launcher
    └── migrate.ps1               # Migration helper
```

---

## 🎬 Quick Start Commands

```bash
# First run (launches wizard automatically)
python desktop_tracker.py

# Or use the batch file
start_tracker.bat

# Re-run setup wizard anytime
python setup_wizard.py

# Set up authentication token
python token_manager.py setup

# Test components
python window_detector.py
python activity_detector.py
python gaming_detector.py
```

---

## 🔧 Setup Wizard Features

### Automatic Detection
- Detects if configuration is needed
- Runs automatically on first `desktop_tracker.py` launch
- Can be re-run anytime with `setup_wizard.py`

### Smart Validation
- ✅ Ensures HTTPS is used (security requirement)
- ✅ Validates URL format
- ✅ Validates device ID format (alphanumeric, hyphens, underscores)
- ✅ Provides helpful defaults and suggestions

### User-Friendly
- Clear prompts and instructions
- Shows examples for each input
- Automatically fixes common mistakes (e.g., adding `https://`)
- Provides immediate feedback on invalid inputs

### Safe Configuration
- Updates `.env` file automatically
- Preserves existing settings you don't change
- Creates `.env` from template if it doesn't exist

---

## 📋 What Gets Configured

The wizard sets up these **required** settings:

| Setting | Description | Example |
|---------|-------------|---------|
| `PHOENIX_API_URL` | Your Phoenix server URL (HTTPS required) | `https://phoenix.example.com` |
| `DEVICE_ID` | Unique device identifier | `desktop-MYCOMPUTER` |

All other settings use sensible defaults and can be customized later in `.env`:
- Capture interval (60s)
- Heartbeat interval (60s)
- Image quality and size
- Gaming process blacklist
- Logging level

---

## 🔐 Next Steps After First Run

### 1. Generate Device Token

From your Phoenix Web Dashboard:
1. Navigate to **Settings → Devices**
2. Click **"Generate New Device Token"**
3. Name it with your Device ID
4. Copy the token

Then store it securely:
```bash
python token_manager.py setup
```

Paste your token when prompted. It will be stored in Windows Credential Manager.

### 2. Run the Tracker

```bash
python desktop_tracker.py
```

You should see:
```
✅ Tracker initialized successfully
Capture interval: 60s
Heartbeat interval: 60s
Press Ctrl+C to stop
```

### 3. Set Up Auto-Start (Optional)

See `INSTALL_WINDOWS.md` for instructions on running the tracker automatically at Windows startup.

---

## 🐛 Troubleshooting

### Wizard doesn't appear
- The wizard only runs if `.env` has placeholder values
- Force it to run: `python setup_wizard.py`

### "PHOENIX_API_URL must use HTTPS protocol"
- The wizard enforces HTTPS for security
- For testing, `http://localhost` is allowed

### "No authentication token found"
- This is normal after initial setup
- Generate a token from Phoenix Dashboard
- Run: `python token_manager.py setup`

### Changes to `.env` not taking effect
- Restart the tracker after editing `.env`
- Check `phoenix_tracker.log` for errors

---

## 📖 Documentation

- **[FIRST_RUN.md](FIRST_RUN.md)** - Detailed first-run guide
- **[README.md](README.md)** - Complete documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference
- **[INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)** - Windows setup guide

---

## ✨ Summary

You now have a fully functional Phoenix Desktop Screen Time Tracker with:

✅ **Automated setup** - No manual configuration required  
✅ **Smart validation** - Catches configuration errors early  
✅ **Secure by default** - Enforces HTTPS, supports Windows Credential Manager  
✅ **User-friendly** - Clear prompts and helpful defaults  
✅ **Production ready** - All features implemented and tested  

**Just run `python desktop_tracker.py` and you're ready to go!** 🚀
