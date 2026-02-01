# Phoenix Tracker - Administrator Access Setup

This guide shows you how to run Phoenix Tracker with administrator privileges.

---

## Why You Might Need Admin Access

- ✅ **Task Scheduler Setup** - Creating scheduled tasks requires admin rights
- ✅ **System-Level Monitoring** - Some window detection features work better with admin
- ✅ **Protected Applications** - Capture data from apps running as admin

> **Note:** For most users, admin access is **NOT required**. The startup shortcut works fine without it.

---

## Method 1: Run Installer as Administrator (Recommended)

This adds the Task Scheduler backup which requires admin privileges.

### Steps:

1. **Open Command Prompt as Administrator:**
   - Press `Win + X`
   - Select **"Terminal (Admin)"** or **"Command Prompt (Admin)"**
   - OR search for "cmd", right-click → "Run as administrator"

2. **Navigate to your project folder:**
   ```cmd
   cd C:\Users\marku\Documents\phoenix-desktop
   ```

3. **Run the installer:**
   ```cmd
   python install_autostart.py
   ```

4. **Select option 2** (Install autostart + Task Scheduler backup)

5. **Done!** Both methods will now be configured.

---

## Method 2: Configure Existing Shortcut to Run as Admin

Make the existing startup shortcut run with elevated privileges.

### Steps:

1. **Open Startup Folder:**
   - Press `Win + R`
   - Type `shell:startup`
   - Press Enter

2. **Modify the shortcut:**
   - Right-click on **"Phoenix Tracker.lnk"**
   - Select **Properties**
   - Click **"Advanced..."** button
   - Check ☑ **"Run as administrator"**
   - Click **OK** → **OK**

### ⚠️ Important Note:

When a startup shortcut runs as admin, Windows will show a **UAC prompt** every time you log in. You'll need to click "Yes" manually. This can be annoying!

---

## Method 3: Task Scheduler with Highest Privileges (Best for Admin)

This is the most reliable way to run with admin privileges automatically, without UAC prompts.

### Option A: Use the Automated Script

```cmd
# Run as Administrator!
python install_autostart_admin.py
```

(I'll create this script for you)

### Option B: Manual Setup

1. **Open Task Scheduler as Admin:**
   - Press `Win + X` → **Terminal (Admin)**
   - Type: `taskschd.msc` and press Enter

2. **Create Task:**
   - Click **"Create Task..."** (not "Create Basic Task")
   - **General tab:**
     - Name: `Phoenix Tracker Tray`
     - Check ☑ **"Run with highest privileges"**
     - Check ☑ **"Run whether user is logged on or not"** (optional)

3. **Triggers tab:**
   - Click **"New..."**
   - Begin the task: **"At log on"**
   - Specific user: **Your username**
   - Click **OK**

4. **Actions tab:**
   - Click **"New..."**
   - Action: **"Start a program"**
   - Program/script: `pythonw.exe`
   - Add arguments: `tray_app.py`
   - Start in: `C:\Users\marku\Documents\phoenix-desktop`
   - Click **OK**

5. **Conditions tab:**
   - Uncheck **"Start only if on AC power"** (for laptops)

6. **Settings tab:**
   - Check ☑ **"Allow task to be run on demand"**
   - Check ☑ **"If the task fails, restart every: 1 minute"**
   - Attempt to restart up to: **3 times**

7. **Click OK** and enter your password if prompted

---

## Method 4: Create Admin Batch File

Create a special launcher that always runs as admin.

### Steps:

Use the provided `start_tray_admin.bat` script (I'll create it for you).

To use:
1. Right-click `start_tray_admin.bat`
2. Select **"Run as administrator"**

To make it auto-run as admin on startup:
1. Create shortcut to `start_tray_admin.bat`
2. Put shortcut in Startup folder (`shell:startup`)
3. Right-click shortcut → Properties → Advanced
4. Check "Run as administrator"

---

## Comparison of Methods

| Method | Auto-runs | Admin Access | UAC Prompt | Difficulty |
|--------|-----------|--------------|------------|------------|
| **Startup Folder** | ✅ Yes | ❌ No | ❌ No | ⭐ Easy |
| **Startup + "Run as Admin"** | ✅ Yes | ✅ Yes | ⚠️ **Every login** | ⭐⭐ Medium |
| **Task Scheduler** | ✅ Yes | ✅ Yes | ❌ No | ⭐⭐⭐ Advanced |
| **Manual Launch as Admin** | ❌ No | ✅ Yes | ⚠️ Each time | ⭐ Easy |

---

## Recommended Approach

### For Most Users:
**Use Task Scheduler** (Method 3)
- ✅ Auto-runs on login
- ✅ Admin privileges
- ✅ No UAC prompts
- ✅ Most reliable

### Quick Setup:
```cmd
# Open Command Prompt as Administrator
python install_autostart_admin.py
```

---

## Troubleshooting

### "Access is denied" when creating Task Scheduler task

**Solution:** You must run as administrator
- Right-click Command Prompt → "Run as administrator"
- Then run the script

### UAC prompt appears every time I log in

**Cause:** Startup shortcut is set to "Run as administrator"

**Solutions:**
1. Use Task Scheduler instead (Method 3)
2. Or remove "Run as administrator" from the shortcut

### Task runs but app doesn't appear

**Check:**
1. Open Task Scheduler
2. Right-click the task → **Run**
3. Check the **"Last Run Result"** column
4. Click the **History** tab to see errors

**Common fixes:**
- Make sure paths are absolute (not relative)
- Verify Python is in PATH
- Check that `tray_app.py` exists

### App needs admin but I don't want UAC prompts

**Use Task Scheduler** with "Run with highest privileges"
- This runs as admin without prompting
- One-time setup
- No UAC every login

---

## Security Considerations

### Do you actually need admin access?

**YES, if:**
- ✅ You want to monitor admin-level applications
- ✅ You want the most reliable Task Scheduler setup
- ✅ You need system-level screen capture

**NO, if:**
- ❌ You only track normal user applications
- ❌ The basic startup shortcut works fine
- ❌ You don't want elevated privileges

### Best Practice:

**Start without admin access.** If you encounter specific apps or windows that don't get tracked, then add admin privileges.

---

## Quick Commands

```cmd
# Run installer as admin (PowerShell)
Start-Process cmd -Verb RunAs -ArgumentList "/c cd C:\Users\marku\Documents\phoenix-desktop && python install_autostart_admin.py"

# Check if running as admin (PowerShell)
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Open Task Scheduler as admin
Start-Process taskschd.msc -Verb RunAs

# Open Startup folder
explorer shell:startup
```

---

## Next Steps

1. **Decide which method you prefer** (I recommend Task Scheduler)
2. **Run the setup as administrator**
3. **Test the configuration**
4. **Verify with:** `python verify_autostart.py`

---

*For automated setup, run: `install_autostart_admin.py` as Administrator*
