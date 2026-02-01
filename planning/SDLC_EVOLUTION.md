# Phoenix Desktop Evolution: SDLC & Roadmap

## 1. Vision & Objective
**Goal:** Evolution from "Passive Observer" (Background Telemetry) to "Active Assistant" (Interactive Companion).
**Source Material:** `Work In Progress - Source.md`
**Key Metaphor:** The transition from a simple data logger to an intelligent "Co-pilot" that intervenes to protect focus and well-being.

## 2. Methodology: RFC-Driven Development
To manage the complexity of this platform shift (Python -> Tauri/Electron), we will adopt an **RFC (Request for Comments)** driven process. major architectural decisions must be proposed, documented, and approved before implementation.

### The RFC Process:
1.  **Draft**: Create an RFC document in `planning/rfcs/`.
2.  **Review**: Analyze trade-offs (Performance vs. Velocity).
3.  **Approve**: Lock the design.
4.  **Implement**: Build according to spec.

## 3. Phased Implementation Roadmap

### Phase 0: Foundation & Architecture (Current)
*Focus: De-risking the tech stack shift.*
*   **Deliverable**: Approved Architecture RFC (RFC-001).
*   **Key Decision**: Architecture Selection (Tauri vs. Electron) & Integration Strategy (Sidecar vs. Rewrite).
*   **Action Items**:
    *   [ ] Analyze Python codebase capability retention.
    *   [ ] Draft `RFC-001-Architecture-Strategy`.
    *   [ ] Select Frontend Stack (React/Vite recommended).

### Phase 1: The "Sidecar" Foundation (The Hybrid Era)
*Focus: Bringing up the new UI while keeping existing logic alive.*
*   **Goal**: A running Desktop App (Tauri/Electron) that launches the existing Python tracker as a subprocess.
*   **Features**:
    *   System Tray management moves to the new App.
    *   "Quick Launchpad" (Menu) implementation (Source Section 3).
    *   Basic bidirectional communication (New App <-> Python Tracker).
    *   **Milestone**: "Phoenix v2.0 Alpha" - Runs, looks better, tracks data same as before.

### Phase 2: Rapid Capture & Input (The "Tool" Layer)
*Focus: High-impact interactive features.*
*   **Goal**: Implement the Global Input capabilities.
*   **Features**:
    *   Global "Omnibox" (Cmd+Space) Frontend.
    *   **Smart Task Logic**: Connect to `phoenix-task-intelligence` for pre-save decomposition. (See [Integration Guide Sec 3](SERVICE_INTEGRATION_GUIDE.md#3-rapid-task-capture)).
    *   **Smart Screenshot**: Implement OCR pipeline via `phoenix-media-processor`. (See [Integration Guide Sec 5](SERVICE_INTEGRATION_GUIDE.md#5-media-services-tts--voice)).
    *   **Milestone**: "Phoenix Companion Beta".

### Phase 3: Context & Insight (The "Mirror" Layer)
*Focus: Visualizing the data we've been collecting.*
*   **Goal**: Real-time feedback loops.
*   **Features**:
    *   Productivity HUD widget.
    *   **Context Restoration**: "What Was I Doing?" Cards via `phoenix-context-graph`. (See [Integration Guide Sec 4](SERVICE_INTEGRATION_GUIDE.md#4-context-restoration-what-was-i-doing)).
    *   Daily Wrap-up Generation.

### Phase 4: Adaptive Interventions (The "Active" Layer)
*Focus: Closing the loop with proactive assistance.*
*   **Goal**: The system nudges the user based on sensing data.
*   **Features**:
    *   **Intervention Engine**: WebSocket connection to `phoenix-adaptive-intervention`. (See [Integration Guide Sec 2](SERVICE_INTEGRATION_GUIDE.md#2-adaptive-interventions-websocket)).
    *   Focus Guard / DND integration.
    *   Meeting Prep prompts.

## 4. Quality Assurance & Standards
*   **Testing**: E2E testing for the UI (Playwright), Unit tests for the Python Logic (Pytest).
*   **CI/CD**: Github Actions for cross-platform builds (if expanding beyond Windows) and Release creation.

## 5. Environment Setup & Prerequisites
To support the Phase 1 Architecture (Tauri + Python), the development environment requires:
*   [x] **Node.js**: Installed (v22+ recommended).
*   [x] **Python**: Installed (v3.11+ recommended).
*   [ ] **Rust**: **REQUIRED** for Tauri. Must install `rustup` for Windows (requires Visual Studio C++ Build Tools).
*   [ ] **Wix Toolset** (Optional): For building MSI installers later.

## 6. Reference Specifications
*   **[Integration Guide](SERVICE_INTEGRATION_GUIDE.md)**: Detailed API specs for connecting to `phoenix-core`, `task-intelligence`, and `adaptive-intervention`.
*   **[RFC 001](rfcs/001-architecture-strategy.md)**: Core sidecar architecture definition.
