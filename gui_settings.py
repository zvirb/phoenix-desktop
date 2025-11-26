"""
GUI Settings Window for Phoenix Desktop Tracker.
Modern Windows 11 styled interface.
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
import socket
from typing import Optional, Callable
from windows_settings import settings_manager
from token_manager import TokenManager
import logging

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Modern settings window for Phoenix Tracker."""
    
    def __init__(self, on_save: Optional[Callable] = None):
        """
        Initialize settings window.
        
        Args:
            on_save: Callback function to call after settings are saved
        """
        self.on_save = on_save
        self.window = None
        self.token_manager = TokenManager()
    
    def show(self):
        """Show the settings window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        self.window = tk.Tk()
        self.window.title("Phoenix Tracker - Settings")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        
        # Configure colors for Windows 11 style
        bg_color = "#F3F3F3"
        card_color = "#FFFFFF"
        accent_color = "#0078D4"
        text_color = "#1F1F1F"
        
        self.window.configure(bg=bg_color)
        
        # Create main frame with padding
        main_frame = tk.Frame(self.window, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        title_label = tk.Label(
            main_frame,
            text="⚙️ Phoenix Tracker Settings",
            font=title_font,
            bg=bg_color,
            fg=text_color
        )
        title_label.pack(pady=(0, 20))
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Server Configuration Section
        self._create_section(scrollable_frame, "Server Configuration", [
            ("Phoenix API URL:", "url", "https://phoenix.example.com"),
            ("Device ID:", "device_id", self._get_default_device_id()),
        ])
        
        # Capture Settings Section
        self._create_section(scrollable_frame, "Capture Settings", [
            ("Capture Interval (seconds):", "capture_interval", "60"),
            ("Heartbeat Interval (seconds):", "heartbeat_interval", "60"),
            ("Similarity Threshold (0-1):", "similarity_threshold", "0.95"),
        ])
        
        # Performance Settings Section
        self._create_section(scrollable_frame, "Performance Settings", [
            ("Max Image Width (pixels):", "max_image_width", "1024"),
            ("JPEG Quality (1-100):", "jpeg_quality", "70"),
        ])
        
        # Security Settings Section
        self._create_section_checkboxes(scrollable_frame, "Security Settings", [
            ("Verify SSL Certificates", "verify_ssl", True),
        ])
        
        # Advanced Settings Section
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self._create_section_dropdown(scrollable_frame, "Advanced Settings", 
                                      "Log Level:", "log_level", log_levels, "INFO")
        
        # Token Management Section
        self._create_token_section(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame at bottom
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Settings",
            command=self._save_settings,
            bg=accent_color,
            fg="white",
            font=font.Font(family="Segoe UI", size=10, weight="bold"),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        save_btn.pack(side="right", padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            bg=card_color,
            fg=text_color,
            font=font.Font(family="Segoe UI", size=10),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        cancel_btn.pack(side="right", padx=5)
        
        # Load current settings
        self._load_settings()
        
        # Center window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        self.window.mainloop()
    
    def _get_default_device_id(self) -> str:
        """Get default device ID based on hostname."""
        hostname = socket.gethostname().lower()
        hostname = ''.join(c if c.isalnum() or c == '-' else '-' for c in hostname)
        return f"desktop-{hostname}"
    
    def _create_section(self, parent, title, fields):
        """Create a settings section with text inputs."""
        # Section frame
        section = tk.LabelFrame(
            parent,
            text=title,
            bg="#FFFFFF",
            font=font.Font(family="Segoe UI", size=11, weight="bold"),
            padx=15,
            pady=15
        )
        section.pack(fill="x", pady=10)
        
        self.entries = getattr(self, 'entries', {})
        
        for label_text, field_name, default_value in fields:
            row = tk.Frame(section, bg="#FFFFFF")
            row.pack(fill="x", pady=5)
            
            label = tk.Label(
                row,
                text=label_text,
                bg="#FFFFFF",
                font=font.Font(family="Segoe UI", size=9),
                width=30,
                anchor="w"
            )
            label.pack(side="left")
            
            entry = tk.Entry(
                row,
                font=font.Font(family="Segoe UI", size=9),
                relief=tk.SOLID,
                borderwidth=1
            )
            entry.pack(side="right", fill="x", expand=True)
            entry.insert(0, default_value)
            
            self.entries[field_name] = entry
    
    def _create_section_checkboxes(self, parent, title, fields):
        """Create a settings section with checkboxes."""
        section = tk.LabelFrame(
            parent,
            text=title,
            bg="#FFFFFF",
            font=font.Font(family="Segoe UI", size=11, weight="bold"),
            padx=15,
            pady=15
        )
        section.pack(fill="x", pady=10)
        
        self.checkboxes = getattr(self, 'checkboxes', {})
        
        for label_text, field_name, default_value in fields:
            var = tk.BooleanVar(value=default_value)
            checkbox = tk.Checkbutton(
                section,
                text=label_text,
                variable=var,
                bg="#FFFFFF",
                font=font.Font(family="Segoe UI", size=9),
                activebackground="#FFFFFF"
            )
            checkbox.pack(anchor="w", pady=5)
            self.checkboxes[field_name] = var
    
    def _create_section_dropdown(self, parent, title, label_text, field_name, options, default):
        """Create a settings section with dropdown."""
        section = tk.LabelFrame(
            parent,
            text=title,
            bg="#FFFFFF",
            font=font.Font(family="Segoe UI", size=11, weight="bold"),
            padx=15,
            pady=15
        )
        section.pack(fill="x", pady=10)
        
        self.dropdowns = getattr(self, 'dropdowns', {})
        
        row = tk.Frame(section, bg="#FFFFFF")
        row.pack(fill="x", pady=5)
        
        label = tk.Label(
            row,
            text=label_text,
            bg="#FFFFFF",
            font=font.Font(family="Segoe UI", size=9),
            width=30,
            anchor="w"
        )
        label.pack(side="left")
        
        var = tk.StringVar(value=default)
        dropdown = ttk.Combobox(
            row,
            textvariable=var,
            values=options,
            state="readonly",
            font=font.Font(family="Segoe UI", size=9)
        )
        dropdown.pack(side="right", fill="x", expand=True)
        
        self.dropdowns[field_name] = var
    
    def _create_token_section(self, parent):
        """Create token management section."""
        section = tk.LabelFrame(
            parent,
            text="Authentication Token",
            bg="#FFFFFF",
            font=font.Font(family="Segoe UI", size=11, weight="bold"),
            padx=15,
            pady=15
        )
        section.pack(fill="x", pady=10)
        
        # Check if token exists
        has_token = self.token_manager.get_token() is not None
        
        status_text = "✅ Token configured" if has_token else "⚠️ No token configured"
        status_label = tk.Label(
            section,
            text=status_text,
            bg="#FFFFFF",
            font=font.Font(family="Segoe UI", size=9),
            fg="#107C10" if has_token else "#D83B01"
        )
        status_label.pack(anchor="w", pady=5)
        
        btn_frame = tk.Frame(section, bg="#FFFFFF")
        btn_frame.pack(fill="x", pady=5)
        
        setup_btn = tk.Button(
            btn_frame,
            text="Setup Token",
            command=self._setup_token,
            bg="#0078D4",
            fg="white",
            font=font.Font(family="Segoe UI", size=9),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        setup_btn.pack(side="left", padx=5)
        
        if has_token:
            delete_btn = tk.Button(
                btn_frame,
                text="Delete Token",
                command=self._delete_token,
                bg="#D83B01",
                fg="white",
                font=font.Font(family="Segoe UI", size=9),
                relief=tk.FLAT,
                padx=20,
                pady=5,
                cursor="hand2"
            )
            delete_btn.pack(side="left", padx=5)
    
    def _load_settings(self):
        """Load settings from Windows Registry."""
        # Load text fields
        if hasattr(self, 'entries'):
            if 'url' in self.entries:
                url = settings_manager.get_phoenix_url()
                if url:
                    self.entries['url'].delete(0, tk.END)
                    self.entries['url'].insert(0, url)
            
            if 'device_id' in self.entries:
                device_id = settings_manager.get_device_id()
                if device_id:
                    self.entries['device_id'].delete(0, tk.END)
                    self.entries['device_id'].insert(0, device_id)
            
            if 'capture_interval' in self.entries:
                interval = settings_manager.get_capture_interval()
                self.entries['capture_interval'].delete(0, tk.END)
                self.entries['capture_interval'].insert(0, str(interval))
            
            if 'heartbeat_interval' in self.entries:
                interval = settings_manager.get_heartbeat_interval()
                self.entries['heartbeat_interval'].delete(0, tk.END)
                self.entries['heartbeat_interval'].insert(0, str(interval))
            
            if 'similarity_threshold' in self.entries:
                threshold = settings_manager.get_similarity_threshold()
                self.entries['similarity_threshold'].delete(0, tk.END)
                self.entries['similarity_threshold'].insert(0, str(threshold))
            
            if 'max_image_width' in self.entries:
                width = settings_manager.get_setting('max_image_width', 1024)
                self.entries['max_image_width'].delete(0, tk.END)
                self.entries['max_image_width'].insert(0, str(width))
            
            if 'jpeg_quality' in self.entries:
                quality = settings_manager.get_setting('jpeg_quality', 70)
                self.entries['jpeg_quality'].delete(0, tk.END)
                self.entries['jpeg_quality'].insert(0, str(quality))
        
        # Load checkboxes
        if hasattr(self, 'checkboxes'):
            if 'verify_ssl' in self.checkboxes:
                verify = settings_manager.get_verify_ssl()
                self.checkboxes['verify_ssl'].set(verify)
        
        # Load dropdowns
        if hasattr(self, 'dropdowns'):
            if 'log_level' in self.dropdowns:
                level = settings_manager.get_log_level()
                self.dropdowns['log_level'].set(level)
    
    def _save_settings(self):
        """Save settings to Windows Registry."""
        try:
            # Validate and save URL
            url = self.entries['url'].get().strip()
            if not url:
                messagebox.showerror("Error", "Phoenix API URL is required")
                return
            
            if not url.startswith('https://') and not url.startswith('http://localhost'):
                messagebox.showerror("Error", "URL must use HTTPS (or http://localhost for testing)")
                return
            
            # Validate and save Device ID
            device_id = self.entries['device_id'].get().strip()
            if not device_id or len(device_id) < 3:
                messagebox.showerror("Error", "Device ID must be at least 3 characters")
                return
            
            # Save basic settings
            settings_manager.save_phoenix_url(url)
            settings_manager.save_device_id(device_id)
            
            # Save intervals
            try:
                capture_interval = int(self.entries['capture_interval'].get())
                if capture_interval < 10:
                    raise ValueError("Capture interval must be at least 10 seconds")
                settings_manager.save_capture_interval(capture_interval)
                
                heartbeat_interval = int(self.entries['heartbeat_interval'].get())
                if heartbeat_interval < 10:
                    raise ValueError("Heartbeat interval must be at least 10 seconds")
                settings_manager.save_heartbeat_interval(heartbeat_interval)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid interval: {e}")
                return
            
            # Save similarity threshold
            try:
                threshold = float(self.entries['similarity_threshold'].get())
                if not 0 <= threshold <= 1:
                    raise ValueError("Similarity threshold must be between 0 and 1")
                settings_manager.save_similarity_threshold(threshold)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid similarity threshold: {e}")
                return
            
            # Save performance settings
            try:
                max_width = int(self.entries['max_image_width'].get())
                if max_width < 100:
                    raise ValueError("Image width must be at least 100 pixels")
                settings_manager.save_setting('max_image_width', max_width)
                
                jpeg_quality = int(self.entries['jpeg_quality'].get())
                if not 1 <= jpeg_quality <= 100:
                    raise ValueError("JPEG quality must be between 1 and 100")
                settings_manager.save_setting('jpeg_quality', jpeg_quality)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid performance setting: {e}")
                return
            
            # Save checkboxes
            if hasattr(self, 'checkboxes'):
                settings_manager.save_verify_ssl(self.checkboxes['verify_ssl'].get())
            
            # Save dropdowns
            if hasattr(self, 'dropdowns'):
                settings_manager.save_log_level(self.dropdowns['log_level'].get())
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
            # Call callback if provided
            if self.on_save:
                self.on_save()
            
            self.window.destroy()
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _setup_token(self):
        """Setup authentication token."""
        token = tk.simpledialog.askstring(
            "Setup Token",
            "Enter your device token from Phoenix Dashboard:",
            parent=self.window
        )
        
        if token:
            if self.token_manager.save_token(token.strip()):
                messagebox.showinfo("Success", "Token saved successfully!")
                # Refresh the window to update token status
                self.window.destroy()
                self.show()
            else:
                messagebox.showerror("Error", "Failed to save token")
    
    def _delete_token(self):
        """Delete authentication token."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the token?"):
            if self.token_manager.delete_token():
                messagebox.showinfo("Success", "Token deleted successfully!")
                # Refresh the window
                self.window.destroy()
                self.show()
            else:
                messagebox.showerror("Error", "Failed to delete token")


# Simple dialog extension
import tkinter.simpledialog


if __name__ == "__main__":
    # Test the settings window
    settings = SettingsWindow()
    settings.show()
