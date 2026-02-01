# RFC 001: Architecture Strategy - Tauri Sidecar Pattern

| Metadata | Details |
| :--- | :--- |
| **Status** | DRAFT |
| **Date** | 2026-02-02 |
| **Topic** | Evolution to Active Assistant Architecture |

## 1. Problem Statement
The current `phoenix-desktop` application is a Python script relying on `pystray` and `customtkinter`. While effective for background telemetry ("Passive Observer"), it lacks the capabilities to render rich, interactive UI elements required for the "Active Assistant" roadmap (Omnibox, HUDs, Floating Widgets) with high performance and low resource footprint.

## 2. Proposed Solution: Tauri + React with Python Sidecar
We propose rebuilding the `phoenix-desktop` client using **Tauri**, while retaining the existing Python logic as a managed **Sidecar**.

### 2.1 The Stack
*   **Host/Shell**: Tauri (Rust). Provides the system tray, global shortcuts, and window management.
*   **UI Layer**: React + Vite + TailwindCSS. Renders the Omnibox, HUD, and Settings.
*   **Logic capabilities**:
    *   **Node/Rust**: Handles UI state, shortcuts, and simple IO.
    *   **Python (Sidecar)**: Handles complex "Sensing" (Window hooks, OCR, Inference, Telemetry) by reusing the existing robust codebase.

### 2.2 The Sidecar Pattern
Tauri provides native "Sidecar" support. We will:
1.  Package the existing implementation (e.g., `tray_app.py` refactored into `headless_tracker.py`) using **PyInstaller** into a single binary.
2.  Configure Tauri to spawn this binary on startup.
3.  Establish an IPC (Inter-Process Communication) channel:
    *   **Telemetry Stream**: Python -> Tauri (via Stdout or ZeroMQ).
    *   **Commands**: Tauri -> Python (via Stdin or ZeroMQ).

### 2.3 Why this approach?
*   **Immediate Value**: We don't spend months rewriting the working telemetry logic in Rust.
*   **Rich UI**: We get full React capabilities for the new features (Omnibox, HUD).
*   **Performance**: Tauri is lighter than Electron.
*   **Gradual Migration**: We can slowly move logic from Python to Rust over time if performance demands it.

## 3. Implementation Plan (Architecture)

### Step 1: Refactor Python for Headless Operation
Modify `tray_app.py` to remove `pystray` and `customtkinter` when running in "Sidecar Mode". It should become a pure CLI tool that:
*   Starts the tracking loops.
*   Outputs events as JSON to Stdout (or a local socket).
*   Accepts commands via Stdin.

### Step 2: Initialize Tauri Project
*   `npm create tauri-app`
*   Configure `tauri.conf.json` to define the sidecar.

### Step 3: Communication Bridge (The Glue)
*   Create a Rust wrapper in Tauri to read the Python Sidecar's output and emit events to the React Frontend.
*   *Example*: Python detects "Flow State" -> Prints JSON -> Rust reads -> Emits `flow-state-detected` event -> React shows "DND Active" badge.

## 4. Alternatives Considered
*   **Electron**: Easier for pure web devs, but significantly heavier RAM usage (critical for a background always-on app).
*   **Pure Rust Rewrite**: Valid long-term goal, but specific libraries (like `mss`, `pywin32` equivalents) might have steep learning curves or missing features, delaying the "Active" features.
*   **Extend Python UI**: `customtkinter` is rigid. Building a "Global Omnibox" or transparent overlays is extremely difficult and non-native feeling compared to a Webview.

## 5. Security Implications
*   The Sidecar runs with the same permissions as the main app.
*   We must ensure the Python binary is signed or verified if distributed.
*   Localhost sockets (if used) must be secured/authenticated to prevent other apps from injecting fake telemetry.
