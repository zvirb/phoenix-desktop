# Phoenix Desktop Integration Guide

This guide details how the Phoenix Desktop App (Rust/Tauri) should integrate with the backend services.

## 1. Authentication
*   **Method**: JWT (Bearer Token).
*   **Source**: Re-use tokens from `phoenix-iam` (shared keychain if possible, or manual login flow).
*   **Header**: `Authorization: Bearer <token>`

## 2. Adaptive Interventions (WebSocket)
*   **Endpoint**: `ws://phoenix-adaptive-intervention:8000/ws/{user_id}`
*   **Protocol**:
    *   **Connect**: Send `Authorization` header or query param.
    *   **Client -> Server (Context Update)**:
        > **Strict Compliance**: Must send `is_agent_activity` to prevent polluting human analytics.
        ```json
        {
          "type": "context_update",
          "context": {
            "status": "active", // "active" | "idle"
            "active_time_seconds": 2750, // Cumulative active time in current session
            "is_agent_activity": false // TRUE if input is simulated (e.g. by agent), FALSE if physical user
          }
        }
        ```
    *   **Server -> Client (Health Nudge)**:
        *Triggered by: `active_time > 45min` AND `!is_agent_activity`*
        ```json
        {
          "type": "health_nudge", // Previously "intervention"
          "data": {
            "id": "micro_break_strain_01",
            "title": "Time to Stretch",
            "message": "You've been active for 45 minutes.",
            "suggestion": "Take a 2-minute break.",
            "action_link": "/emotion/strategies",
            "severity": "medium"
          }
        }
        ```
    *   **Fusion Bridge (Backend Internal)**:
        *   The Desktop client does *not* send to Fusion directly.
        *   `phoenix-adaptive-intervention` forwards validated human activity to `phoenix-multimodal-analytics-fusion:8083`.

## 3. Rapid Task Capture
*   **Goal**: Break down tasks *before* saving them.
*   **Endpoint**: `POST http://phoenix-task-intelligence:8000/api/v1/preview-decompose`
*   **Payload**:
    ```json
    {
      "task_id": "temp-123",
      "task_title": "Fix the login bug",
      "user_id": "...",
      "estimated_minutes": 60
    }
    ```
*   **Response**: Returns list of subtasks. Desktop app should show these in a "Preview" card, allow user to edit, then submit to the *real* `decompose` endpoint or `phoenix-task-intelligence` directly.

## 4. Context Restoration ("What was I doing?")
*   **Goal**: Show a snapshot of previous work state.
*   **Endpoint**: `GET http://phoenix-context-graph:8000/api/v1/context/snapshot?lookback_hours=4`
*   **Response**: Returns a graph summary.
    *   **Key Fields**:
        *   `summary.screen_context`: Last known screen activity.
        *   `summary.recent_completions`: Tasks finished recently.
        *   `nodes`: Check for `type: "document"` or `type: "url"` to offer "Open" links.

## 5. Media Services (TTS & Voice)
*   **Text-to-Speech**:
    *   **Endpoint**: `POST http://phoenix-media-processor:8000/synthesize/audio`
    *   **Payload**: `{"text": "...", "voice": "default"}`
    *   **Usage**: "Read this article" feature.
*   **Smart Screenshot (OCR)**:
    *   **Endpoint**: `POST http://phoenix-media-processor:8000/capture/ocr`
    *   **Payload**: Multipart form data with image file.

## 6. Frontend Quick Links
Map these desktop actions to Deep Links (open in default browser):
*   **Focus Mode**: `https://phoenix.aiwfe.com/focus`
*   **Crisis Help**: `https://phoenix.aiwfe.com/emotion/crisis`
*   **Daily Log**: `https://phoenix.aiwfe.com/journal`
