# Windows Installation Guide

This guide shows you how to set up the Phoenix Desktop Tracker (System Tray App) to run automatically on Windows.

## Option 1: Startup Folder (Recommended)

This is the easiest and most reliable method for the system tray application.

### Step 1: Open Startup Folder

1. Press `Win + R` on your keyboard
2. Type `shell:startup`
3. Press Enter

### Step 2: Create Shortcut

1. Navigate to your `phoenix-desktop` folder
2. Right-click on `start_tray.bat`
3. Select **"Create shortcut"** or **"Show more options" > "Create shortcut"**
4. Move the newly created shortcut to the Startup folder you opened in Step 1

### Step 3: Verify

1. Restart your computer or log out and log back in
2. The Phoenix Tracker icon should appear in your system tray (bottom right) automatically

## Option 2: Task Scheduler

If you prefer using Task Scheduler:

### Step 1: Open Task Scheduler

1. Press `Win + R`
2. Type `taskschd.msc`
3. Press Enter

### Step 2: Create Task

1. Click **"Create Basic Task..."**
2. Name: `Phoenix Tracker Tray`
3. Trigger: **"When I log on"**
4. Action: **"Start a program"**
5. Program/script: Browse to `start_tray.bat` in your `phoenix-desktop` folder
6. Click **Finish**

### Step 3: Configure Properties

1. Find the task in the list
2. Right-click > **Properties**
3. On **General** tab: Check **"Run with highest privileges"**
4. On **Conditions** tab: Uncheck **"Start the task only if the computer is on AC power"** (for laptops)
5. Click **OK**

## Troubleshooting

### App doesn't start
- Check if `pythonw.exe` is running in Task Manager
- Try running `start_tray.bat` manually to see if there are errors
- Check `phoenix_tracker.log` for details

### Icon is hidden
- Windows often hides tray icons by default
- Click the `^` arrow in the system tray
- Drag the Phoenix icon to the main taskbar area to keep it visible

## Uninstallation

1. **Stop the app**: Right-click tray icon > **Exit**
2. **Remove startup item**: Delete the shortcut from `shell:startup`
3. **Delete token**: Run `python token_manager.py delete`
4. **Remove files**: Delete the `phoenix-desktop` folder
