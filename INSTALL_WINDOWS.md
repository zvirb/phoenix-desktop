# Windows Installation Guide

This guide shows you how to set up the Phoenix Desktop Tracker to run automatically on Windows.

## Option 1: Task Scheduler (Recommended)

This method runs the tracker automatically when you log in.

### Step 1: Create a Batch File

Create a file called `start_tracker.bat` in the tracker directory:

```batch
@echo off
cd /d "%~dp0"
python desktop_tracker.py
pause
```

### Step 2: Open Task Scheduler

1. Press `Win + R`
2. Type `taskschd.msc`
3. Press Enter

### Step 3: Create a New Task

1. Click **"Create Task..."** (not "Create Basic Task")
2. On the **General** tab:
   - Name: `Phoenix Desktop Tracker`
   - Description: `Screen time tracking for Phoenix Digital Homestead`
   - Select: **"Run whether user is logged on or not"**
   - Check: **"Do not store password"** (if you want it visible)
   - Select: **"Run only when user is logged on"** (for GUI access)

### Step 4: Configure Triggers

1. Go to **Triggers** tab
2. Click **"New..."**
3. Begin the task: **"At log on"**
4. Select your user account
5. Check: **"Enabled"**
6. Click **OK**

### Step 5: Configure Actions

1. Go to **Actions** tab
2. Click **"New..."**
3. Action: **"Start a program"**
4. Program/script: `pythonw.exe` (to run without console) or `python.exe` (to see console)
5. Add arguments: `desktop_tracker.py`
6. Start in: `C:\path\to\phoenix-tracker` (your tracker directory)
7. Click **OK**

### Step 6: Configure Conditions (Optional)

1. Go to **Conditions** tab
2. Uncheck: **"Start the task only if the computer is on AC power"** (for laptops)
3. You may want to check: **"Start only if the following network connection is available"**

### Step 7: Configure Settings

1. Go to **Settings** tab
2. Check: **"Allow task to be run on demand"**
3. Check: **"Run task as soon as possible after a scheduled start is missed"**
4. Check: **"If the running task does not end when requested, force it to stop"**
5. If the task is already running: **"Do not start a new instance"**

### Step 8: Save and Test

1. Click **OK** to save
2. Find your task in the list
3. Right-click and select **"Run"**
4. The tracker should start

## Option 2: Windows Service (Advanced)

For running the tracker as a true Windows service using NSSM (Non-Sucking Service Manager).

### Step 1: Download NSSM

1. Download from: https://nssm.cc/download
2. Extract to a folder (e.g., `C:\nssm`)
3. Add to PATH or use full path

### Step 2: Install Service

Open PowerShell as Administrator:

```powershell
cd C:\path\to\phoenix-tracker

# Install the service
nssm install PhoenixTracker "C:\Python\python.exe" "C:\path\to\phoenix-tracker\desktop_tracker.py"

# Configure the service
nssm set PhoenixTracker AppDirectory "C:\path\to\phoenix-tracker"
nssm set PhoenixTracker DisplayName "Phoenix Desktop Tracker"
nssm set PhoenixTracker Description "Screen time tracking for Phoenix Digital Homestead"
nssm set PhoenixTracker Start SERVICE_AUTO_START

# Set up logging
nssm set PhoenixTracker AppStdout "C:\path\to\phoenix-tracker\service_output.log"
nssm set PhoenixTracker AppStderr "C:\path\to\phoenix-tracker\service_error.log"

# Start the service
nssm start PhoenixTracker
```

### Managing the Service

```powershell
# Check status
nssm status PhoenixTracker

# Stop the service
nssm stop PhoenixTracker

# Restart the service
nssm restart PhoenixTracker

# Remove the service
nssm remove PhoenixTracker confirm
```

## Option 3: Startup Folder (Simple)

The easiest method, but the tracker window will be visible.

### Step 1: Create Shortcut

1. Right-click `desktop_tracker.py`
2. Select **"Create shortcut"**

### Step 2: Move to Startup Folder

1. Press `Win + R`
2. Type `shell:startup`
3. Press Enter
4. Move the shortcut to this folder

### Step 3: Configure Shortcut (Optional)

1. Right-click the shortcut
2. Select **"Properties"**
3. In **Target**, add `pythonw.exe` before the path to hide the console:
   ```
   C:\Python\pythonw.exe "C:\path\to\phoenix-tracker\desktop_tracker.py"
   ```
4. Click **OK**

## Verifying the Installation

After setup, verify the tracker is running:

### Method 1: Task Manager

1. Press `Ctrl + Shift + Esc`
2. Go to **Details** tab
3. Look for `python.exe` or `pythonw.exe`
4. Check the command line contains `desktop_tracker.py`

### Method 2: Check Logs

Open `phoenix_tracker.log` in the tracker directory:

```powershell
Get-Content phoenix_tracker.log -Tail 20
```

You should see recent heartbeat and capture messages.

### Method 3: Phoenix Dashboard

Log into your Phoenix Dashboard and check the Screen Time section for recent activity.

## Stopping the Tracker

### If running from Task Scheduler:

1. Open Task Scheduler
2. Find "Phoenix Desktop Tracker"
3. Right-click > **Disable** or **Delete**

### If running as a service:

```powershell
nssm stop PhoenixTracker
```

### If running from Startup folder:

1. Press `Win + R`
2. Type `shell:startup`
3. Delete the shortcut
4. Kill the process in Task Manager

## Updating the Tracker

1. Stop the tracker using one of the methods above
2. Update the files (git pull or copy new files)
3. Install any new dependencies:
   ```powershell
   pip install -r requirements.txt -U
   ```
4. Start the tracker again

## Troubleshooting

### Tracker doesn't start at login

- Check Task Scheduler > Task History for errors
- Verify Python path is correct in the task configuration
- Make sure the working directory is set correctly

### "Python not found" error

- Use full path to `python.exe` in task configuration
- Example: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`

### Tracker starts but immediately stops

- Check `phoenix_tracker.log` for errors
- Verify `.env` configuration
- Test manually first: `python desktop_tracker.py`

### High resource usage

- Increase `CAPTURE_INTERVAL` in `.env`
- Use `pythonw.exe` instead of `python.exe` to hide console

### Can't find the log file

Log file is created in the same directory as `desktop_tracker.py`. If running as a service, check the NSSM log locations configured earlier.

## Security Considerations

### Running as Different User

If you want the service to run under a specific user account:

```powershell
nssm set PhoenixTracker ObjectName "DOMAIN\Username" "Password"
```

### Restricted Permissions

The tracker needs:
- Read/write access to its directory (for logs)
- Network access (HTTPS to Phoenix backend)
- Screen capture permissions
- Access to Windows Credential Manager (for token storage)

### Firewall Rules

Ensure Windows Firewall allows:
- Outbound HTTPS (port 443) to your Phoenix server

You can add a rule:

```powershell
New-NetFirewallRule -DisplayName "Phoenix Tracker" `
  -Direction Outbound `
  -Protocol TCP `
  -RemotePort 443 `
  -Action Allow `
  -Program "C:\Python\python.exe"
```

## Uninstallation

### Complete Removal

1. Stop and remove the scheduled task or service (see above)
2. Delete stored token:
   ```powershell
   python token_manager.py delete
   ```
3. Remove the tracker directory
4. (Optional) Uninstall Python packages:
   ```powershell
   pip uninstall -r requirements.txt -y
   ```

That's it! Your Phoenix Desktop Tracker is now installed and running automatically on Windows.
