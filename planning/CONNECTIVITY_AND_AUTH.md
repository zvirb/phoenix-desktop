# Connectivity & Authentication Flow

## 1. Overview
The Phoenix Desktop Companion connects to the remote Phoenix Stack using a **Hybrid Authentication Flow**.
This flow ensures secure, authenticated access to the API services while maintaining a persistent identity on the client device.

## 2. Token Generation & Storage

### Generation
*   **Where**: Phoenix Web Dashboard -> Settings -> Devices.
*   **Action**: "Generate New Device Token".
*   **Format**: A generic string, prefixed with `phx_` (e.g., `phx_aX9...`).
*   **Security**: This is a **Long-Lived Secret**. It functions like an API Key but is tied to a specific device identity.

### Storage (Client-Side)
*   **Mechanism**: Windows Credential Manager.
*   **Key**: `PhoenixTracker_<DEVICE_ID>` (e.g., `PhoenixTracker_DESKTOP-123`).
*   **Safety**: Stored securely at the OS level; not in plain text files (unless fallback mode is triggered).
*   **Interaction**: Managed by `token_manager.py` (Client Lib).

### Verification (Server-Side)
*   **Service**: `phoenix-iam`.
*   **Table**: `device_tokens`.
*   **Validation**: The server stores a **Hash** of the token. The plain token is never stored on the server.

## 3. Authentication Flow (The "Handshake")

When the Desktop App starts (`headless_tracker.py`), it performs the following handshake:

1.  **Retrieve Identity**:
    *   Loads `DEVICE_ID` from Registry/Config.
    *   Loads `Device Token` (`phx_...`) from Windows Credential Manager.

2.  **Authenticate (Exchange)**:
    *   **Request**: `POST /api/v1/devices/authenticate`
    *   **Header**: `Authorization: Bearer <phx_token>`
    *   **Payload**: Device Metadata (IP, Hostname).

3.  **Receive Session**:
    *   **Response**: 
        ```json
        {
          "valid": true,
          "access_token": "eyJhbGciOi...",  // JWT (Short-Lived)
          "expires_in": 600,
          "user": { ... }
        }
        ```
    *   **Critical Detail**: The server returns a **JWT (JSON Web Token)**.

4.  **Session Management**:
    *   The **Sidecar** (`headless_tracker.py`) stores this `access_token` in memory.
    *   It emits the `access_token` to the **Frontend** (`App.tsx`) via the `ready` event.

## 4. Gaining Access to the Stack

To decompose a task, capture a screenshot, or sync context, the app must use the **JWT**:

*   **Correct Usage**:
    *   `Authorization: Bearer <JWT_ACCESS_TOKEN>`
    *   Target: `phoenix-task-intelligence`, `phoenix-core`, etc.

*   **Incorrect Usage (Pre-Fix)**:
    *   Sending `Authorization: Bearer <phx_token>` directly to other services.
    *   Result: `401 Unauthorized` or Connection Refused.

## 5. Troubleshooting Connectivity

If the app reports "Error" or "Connecting...", check:

1.  **DNS & Network**:
    *   Can you ping the API host (`phoenix.aiwfe.com`)?
    *   Is the host reachable from your network? (Cloudflare Access/VPN).

2.  **Token Validity**:
    *   Use the "Reset Token" feature in `token_manager.py` (CLI) or the App Settings to re-paste a fresh token from the Web Dashboard.

3.  **Clock Sync**:
    *   Ensure the Client PC time is synchronized. JWTs have strict `exp` (expiration) and `nbf` (not before) claims.

## Summary of Recent Fixes
*   **Sidecar**: Now correctly extracts and stores the JWT from the initial handshake.
*   **Frontend**: Now receives the JWT for its own API calls.
*   **Logging**: Enhanced to show full error tracebacks in the UI.
