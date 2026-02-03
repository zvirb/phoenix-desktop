# Phoenix Desktop Sidebar - Architecture & SDLC

## 1. Vision & Core Philosophy

The Phoenix Desktop Sidebar is an **Application Desktop Toolbar (AppBar)** that creates a persistent, reserved vertical space on the user's desktop. It is **not** a floating window; it is a system-level dock that resizes the available work area, ensuring user windows tile respectfullly alongside it.

**Core Tenets:**
*   **"Reserved Real Estate"**: It claims its pixels. It does not overlay content.
*   **"System Awareness"**: It scales its UI density based on "Focus" (Sidebar) vs "Background" (Collapsed).
*   **"Bi-Directional Mesh"**: It is both a sensor (Context In) and a controller (Action Out).
*   **"Trust through Visibility"**: Every captured event (screen, window, idle) is visible in the activity feed.

---

## 2. Technical Stack

*   **Runtime:** Python 3.10+
*   **GUI Framework:** `PyQt6` (Required for native AppBar/Docking functionality which CustomTkinter lacks).
    *   *Why PyQt6?* It provides robust access to Windows API (`SHAppBarMessage`) for creating true desktop toolbars that reserve screen space.
*   **Styling:** QSS (Qt Style Sheets) with Tailwind-inspired design tokens.
*   **Backend Integration:** Existing `api_client.py` structure (refactored for async Qt).
*   **Local State:** SQLite (for history/offline queue) + Windows Registry (config).

---

## 3. Architecture Modules

### A. Core Window Manager (`main.py`)
*   Handles the `SHAppBarMessage` registration to reserve screen space.
*   Manages "Docked" (Expanded) vs "Autohide" (Collapsed) states.
*   Global Event Bus for component communication.

### B. The "Handshake" (Onboarding)
*   First-run wizard flow.
*   Validates Server URL, Token, and local dependencies (Ollama, Tailscale).
*   **UI:** Modal Wizard.

### C. The Status HUD (Header)
*   Top-level indicators: Heartbeat pulse, Eye (Visual Context), Brain (Local Inference), Shield (Mesh IP).
*   **UI:** Compact, high-density icon row.

### D. The Activity Stream (Middle)
*   Scrollable list of "Context Cards".
*   Cards: Screenshot, App Focus Change, Idle Event, System Alert.
*   **Features:** Hover to delete/redact.
*   **UI:** Virtualized list view.

### E. The Control Deck (Footer)
*   Quick actions: "War Room", "Block Distractions".
*   Gamification Ticker: XP Bar, Current Streak.
*   Voice Visualizer: Audio waveform (when active).

---

## 4. Implementation Stages

### Phase 1: Foundation (The Shell)
*   [x] Set up standard PyQt6 project structure.
*   [x] Implement `AppBarWindow` class using `ctypes` and `SHAppBarMessage`.
*   [x] Verify screen reservation works (windows resize away from it).
*   [x] Basic expansion/collapse animation (Toggle Logic implemented).

### Phase 2: Design System (The Look)
*   [x] Port Tailwind color palette to `styles.qss` (Initial Pass).
*   [x] Create reusable components: `PhoenixCard` (ActivityCard), `StatusBadge`, `XpBar` (ControlDeck).
*   [ ] Implement "Cyber/War Room" and "Zen" themes.

### Phase 3: Intelligence Integration (The Brain)
*   [x] Connect `ActivityDetector` and `WindowDetector` signals to the Activity Stream (`ContextWorker`).
*   [x] Wire up `APIClient` for real-time auth and heartbeat (`MeshWorker`/`SyncWorker`).
*   [x] Implement the "Handshake" wizard with validation logic (`OnboardingView`).
*   [x] Ensure "War Room" button is connected (Basic logging).

### Phase 4: Mesh Capabilities (The Reach)
*   [ ] "Agent Status" visualization (mocked then connected).
*   [ ] Voice Service waveform visualization.
*   [ ] Inter-process communication for "Gaming Mode" auto-dismiss.

---

## 5. Directory Structure

```
phoenix-desktop/
├── main_sidebar.py           # Entry point
├── phoenix/
│   ├── __init__.py
│   ├── core/
│   │   ├── app_bar.py        # Windows API Docking Logic
│   │   ├── event_bus.py      # Signal/Slot manager
│   │   └── theme_manager.py  # QSS Loader
│   ├── ui/
│   │   ├── main_window.py    # Main UI Shell
│   │   ├── styles.qss        # Tailwind-like Styles
│   │   ├── components/       # Atomic Widgets
│   │   │   ├── status_hud.py
│   │   │   ├── activity_feed.py
│   │   │   ├── control_deck.py
│   │   │   └── xp_bar.py
│   │   └── views/            # Major Views
│   │       ├── onboarding.py
│   │       └── settings.py
│   ├── services/
│   │   ├── context_worker.py  # QThread for Screenshots/Window
│   │   └── mesh_worker.py     # QThread for API/Ollama
│   └── assets/                # Icons/Images
```
