# Guide: Adding the Token Frontend Page

This guide documents the implementation of the "Token" page in the Phoenix Desktop Tracker settings window (`gui_settings.py`). This page allows users to manage their authentication token securely.

## 1. Overview

The Token page provides a user interface for:
- Viewing the current token status (Configured/Not Configured).
- Setting up a new token (via input dialog).
- Deleting an existing token.
- Navigating to the Phoenix Dashboard to generate a token.

## 2. Backend Prerequisites

Before building the UI, we rely on `token_manager.py` to handle the secure storage of the token.

- **Class**: `TokenManager`
- **Methods used**:
    - `get_token()`: To check if a token exists.
    - `save_token(token)`: To securely store the token.
    - `delete_token()`: To remove the token.

Ensure `TokenManager` is imported in `gui_settings.py`:
```python
from token_manager import TokenManager
```

## 3. Implementation Steps

### Step 1: Initialize TokenManager

In the `__init__` method of `ModernSettingsWindow`, we initialize the `TokenManager` instance:

```python
def __init__(self, on_save: Optional[Callable] = None):
    # ...
    self.token_manager = TokenManager()
    # ...
```

### Step 2: Add Navigation Item

We add the "Token" page to the navigation sidebar in the `_create_layout` method. This ensures the user can access the page.

```python
nav_items = [
    # ... other pages ...
    ("token", "🔑 Token", self._show_token_page),
    # ...
]
```

### Step 3: Create the Page Layout (`_show_token_page`)

We define the `_show_token_page` method to render the UI. This method:
1.  Clears the current content.
2.  Sets the active navigation state.
3.  Displays the header.
4.  Checks the token status using `self.token_manager.get_token()`.
5.  Renders the status label and action buttons.

```python
def _show_token_page(self):
    self._clear_content()
    self._set_active_nav("token")
    
    self._create_page_header(self.content_frame, "Authentication", "Manage your device token")
    
    card = self._create_setting_card(self.content_frame, "Device Token")
    
    # Check status
    has_token = self.token_manager.get_token() is not None
    
    # Display Status (Green for success, Orange for warning)
    # ... (See code for full implementation)
    
    # Add Buttons: Setup, Get Token, Delete (if token exists)
    # ...
```

### Step 4: Implement Action Methods

We implement the handler methods for the buttons:

#### `_setup_token`
Prompts the user for a token and saves it.
```python
def _setup_token(self):
    token = tk.simpledialog.askstring("Setup Token", "Enter your device token...")
    if token:
        if self.token_manager.save_token(token.strip()):
            messagebox.showinfo("Success", "Token saved!")
            self._show_token_page()  # Refresh UI
```

#### `_delete_token`
Asks for confirmation and deletes the token.
```python
def _delete_token(self):
    if messagebox.askyesno("Confirm", "Delete token?"):
        self.token_manager.delete_token()
        self._show_token_page()  # Refresh UI
```

#### `_open_token_url`
Opens the web browser to the Phoenix Dashboard.
```python
def _open_token_url(self):
    url = settings_manager.get_phoenix_url()
    # ... validation ...
    webbrowser.open(f"{url}/settings/devices")
```

## 4. Summary

By following this pattern, we created a secure and user-friendly interface for managing authentication tokens. The separation of concerns (UI in `gui_settings.py`, logic in `token_manager.py`) ensures the code remains clean and maintainable.
