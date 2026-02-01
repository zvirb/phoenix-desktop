# Phoenix Desktop Companion: Feature Roadmap
## From Passive Observer to Active Assistant

This document outlines potential features for the Phoenix Desktop App, evolving it from a background telemetry daemon into an interactive AI companion that enhances focus, well-being, and productivity.

### 1. Adaptive Interventions (The "Active" Layer)
*Leveraging `phoenix-phenotyping` and `phoenix-emotional-regulation-coach` to intervene at the right moment.*

*   **Micro-Break Prompts:**
    *   **Trigger:** High keystroke/mouse usage duration > 45 mins OR detected "stress" pattern (rapid switching, erratic movement).
    *   **Action:** Subtle non-modal notification suggesting a 2-minute stretch or breathing exercise.
    *   **Link:** Quick link to `/emotion/strategies` for guided exercises.
*   **Focus Guard / Flow State Protection:**
    *   **Trigger:** Detection of "Flow State" (consistent application usage, high output).
    *   **Action:** Automatically enable DND (Do Not Disturb) on system. Block distraction sites/apps temporarily.
    *   **Visual:** Status bar icon turns a calming color (e.g., Deep Blue).
*   **Context Switching Alerts:**
    *   **Trigger:** Rapidly switching between >5 windows in <1 minute (Fragmented Attention).
    *   **Action:** "You seem distracted. Do you want to capture your current state and clear your mind?" -> Opens Quick Capture.
*   **Meeting Preparation Nudge:**
    *   **Trigger:** 5 minutes before a calendar event (via `phoenix-google-integration`).
    *   **Action:** Pop up a "Pre-flight" card with meeting context, attendee bios, and last related notes.
    *   **Link:** Deep link to `/google/calendar`.

### 2. Rapid Capture & Input (The "Tool" Layer)
*Low-friction interfaces to feed `phoenix-ingestor` and `phoenix-task-intelligence`.*

*   **Global "Omnibox" (Cmd+Space equivalent):**
    *   **Feature:** A floating input bar accessible from anywhere.
    *   **Capabilities:**
        *   **Quick Note:** "Buy milk" -> Saved to Inbox (`/tasks`).
        *   **Smart Task:** "Fix bug in API @tomorrow" -> pre-processed by `phoenix-task-intelligence/decomposer` to break down subtasks before saving.
        *   **Memory:** "Meeting with John: he likes hiking" -> Sent to `phoenix-semantic-memory`.
*   **Smart Screenshot:**
    *   **Feature:** Screenshot tool that doesn't just save an image.
    *   **Process:** OCRs the text, analyzes the UI context (e.g., "Error message in VS Code"), and offers to "Fix this error" or "Save to Knowledge Base".
*   **Voice Command Center:**
    *   **Feature:** Global hotkey to record audio.
    *   **Integration:**
        *   **Voice Notes:** Streamed to `phoenix-audio-streaming` for transcription.
        *   **"Read to Me":** Use `phoenix-media-processor/tts` to read selected text or articles aloud while you work on something else.

### 3. Quick Launchpad (Frontend Shortcuts)
*Direct access to deep web routes from the system tray.*

*   **Focus & Flow:**
    *   `Force Focus Mode` -> Opens `/focus`
    *   `ADHD Tools` -> Opens `/adhd-focus`
    *   `Time Oracle` -> Opens `/time-oracle` (Check predicted energy levels)
*   **Health & Emotion:**
    *   `Check In` -> Opens `/emotional-checkin`
    *   `Crisis Support` -> Opens `/emotion/crisis` (Immediate help)
    *   `Coach` -> Opens `/emotion/coach`
*   **Work & Admin:**
    *   `Task Dashboard` -> Opens `/task-management`
    *   `Project Board` -> Opens `/project-management`
    *   `CRM` -> Opens `/crm`

### 4. Context & Insight (The "Mirror" Layer)
*Visualizing `phoenix-context-graph` data in real-time.*

*   **"What Was I Doing?" (Context Restoration):**
    *   **Scenario:** You return to your desk after a break.
    *   **Feature:** A summary card: "You were debugging `api.py`. You left off looking at the StackOverflow page about 'AsyncIO timeouts'."
    *   **Action:** One-click "Restore Context".
*   **Productivity HUD:**
    *   **Feature:** Minimalist desktop widget showing:
        *   Current Focus Score (from `phoenix-phenotyping`).
        *   Time until next meeting.
        *   Current objective (pinned task).
*   **Daily "Wrap-Up" Generator:**
    *   **Feature:** At 5 PM, generates a bulleted list of accomplishments.
    *   **Integration:** Pulls from `phoenix-journal` and `phoenix-workflow-orchestrator` execution history.

### 5. Desktop-as-a-Trigger (Workflow Integration)
*Using the desktop state to drive `phoenix-workflow-orchestrator`.*

*   **Idle Triggers:**
    *   "User away for 15 mins" -> Trigger "Pause Music" and "Set Slack status to Away".
*   **App-Specific Triggers:**
    *   "Opened VS Code" -> Trigger "Focus Mode" (Close Slack, Start 'Coding' Playlist).
*   **Meeting Mode:**
    *   "Zoom Launched" -> Trigger "Meeting Lights" (via `phoenix-home-assistant`), "Mute Notifications".

### 6. Technical Architecture Proposal

*   **Client Stack:** Tauri (Rust + React) or Electron.
*   **Communication:**
    *   **Telemetry (Out):** UDP/gRPC to `phoenix-ingestor` (low latency).
    *   **Interventions (In):** WebSocket connection to `phoenix-adaptive-intervention`.
*   **Authentication:** Re-use `phoenix-iam` tokens via system keychain.