# Guide: Building the Frontend Token Generation Page

This guide serves as a specification for an LLM Agent (or developer) to build the "Device Tokens" page in the Phoenix Web Dashboard. This page is critical for the Phoenix Desktop Tracker authentication flow.

## 1. Objective

Create a settings page where users can manage their "Device Tokens". These tokens are used by the Phoenix Desktop Tracker to authenticate with the backend.

**Target URL**: `/settings/devices`

## 2. Technical Stack (Assumed)

*   **Framework**: Next.js (App Router)
*   **UI Library**: React
*   **Styling**: Tailwind CSS
*   **Icons**: Lucide React
*   **Components**: Shadcn UI (or similar headless UI components)

## 3. Functional Requirements

### 3.1. Device List
*   Display a list of active devices/tokens.
*   **Columns**:
    *   **Name**: The user-friendly name (e.g., "Work Laptop").
    *   **Device ID**: The unique identifier (e.g., `desktop-marku-pc`).
    *   **Created**: Date of creation.
    *   **Last Active**: When the device last sent a heartbeat.
    *   **Actions**: Revoke/Delete button.

### 3.2. Generate New Token
*   **Trigger**: A "Generate New Token" button (primary action).
*   **Interaction**: Opens a Modal/Dialog.
*   **Input**: "Device Name" (Required).
*   **Process**:
    1.  User enters name.
    2.  Frontend calls `POST /api/devices`.
    3.  Backend generates a secure token (JWT or long-lived API key).
    4.  Backend returns the token **only once**.
*   **Display**:
    *   Show the token in a read-only text area.
    *   Include a "Copy to Clipboard" button.
    *   **Warning**: "Make sure to copy your personal access token now. You won't be able to see it again!"

### 3.3. Revoke Token
*   **Trigger**: "Revoke" or "Delete" button on a list item.
*   **Interaction**: Confirmation Dialog ("Are you sure? This will stop the device from tracking.").
*   **Process**: Call `DELETE /api/devices/:id`.

## 4. API Specification (Reference)

The frontend should interact with the following backend endpoints (to be implemented if missing):

### `GET /api/devices`
Returns a list of devices.
```json
[
  {
    "id": "dev_123",
    "name": "Work Laptop",
    "device_id": "desktop-work-laptop",
    "last_active": "2023-10-27T10:00:00Z",
    "created_at": "2023-10-01T09:00:00Z"
  }
]
```

### `POST /api/devices`
Creates a new device token.
**Request**:
```json
{
  "name": "Gaming PC"
}
```
**Response**:
```json
{
  "id": "dev_456",
  "name": "Gaming PC",
  "token": "phx_live_abc123..." // SHOWN ONLY ONCE
}
```

### `DELETE /api/devices/:id`
Revokes the token.

## 5. Implementation Prompt for Agent

Use the following prompt to instruct an Agent to build this page:

> **Task**: Create the Device Settings page for Phoenix Dashboard.
>
> **File**: `app/settings/devices/page.tsx` (and necessary components).
>
> **Requirements**:
> 1.  Create a responsive page layout with a header "Device Management".
> 2.  Fetch the list of devices from `GET /api/devices` and display them in a table or card grid.
> 3.  Implement a "Generate Token" button that opens a Dialog.
> 4.  Inside the Dialog, allow the user to name the device.
> 5.  On submit, call `POST /api/devices`.
> 6.  **Crucial**: When the response comes back, switch the Dialog content to show the generated `token`. Add a copy button. Do not close the dialog until the user clicks "Done".
> 7.  Implement the "Revoke" button with a confirmation alert.
> 8.  Use Tailwind CSS for styling. Make it look premium (dark mode compatible).
> 9.  Handle loading states and error toasts.

## 6. Design Guidelines

*   **Aesthetics**: Clean, modern, "Linear-style" or "Vercel-style" design.
*   **Colors**: Slate/Zinc for neutrals, Blue/Indigo for primary actions, Red for destructive actions.
*   **Feedback**: Use toast notifications for "Token Copied" and "Device Revoked".
