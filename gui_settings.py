"""
Modern Windows 11 Settings Window for Phoenix Desktop Tracker.
Follows 2025 Fluent Design System guidelines with comprehensive error logging.
"""
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import socket
from typing import Optional, Callable
from windows_settings import settings_manager
from token_manager import TokenManager
from phoenix_logging import get_logger, logged_method, log_exception

logger = get_logger(__name__)


class ModernSettingsWindow:
    """
    Modern Windows 11 styled settings window.
    Implements 2025 Fluent Design System principles:
    - Rounded corners and soft visuals
    - Clear information hierarchy with hero controls
    - Left navigation pane
    - Segoe UI Variable font
    - Calm, uncluttered experience
    - Enhanced accessibility
    """
    
    def __init__(self, on_save: Optional[Callable] = None):
        """
        Initialize settings window.
        
        Args:
            on_save: Callback function to call after settings are saved
        """
        logger.info("Initializing Modern Settings Window")
        self.on_save = on_save
        self.window = None
        self.token_manager = TokenManager()
        self.current_page = "server"  # Track current page
        
        # Windows 11 2025 Fluent Design Colors
        self.colors = {
            'bg_primary': '#F3F3F3',        # Light gray background
            'bg_secondary': '#FAFAFA',      # Slightly lighter
            'card': '#FFFFFF',              # White cards
            'accent': '#0078D4',            # Windows blue
            'accent_hover': '#106EBE',      # Darker blue on hover
            'text_primary': '#1F1F1F',      # Almost black
            'text_secondary': '#616161',    # Gray text
            'border': '#E5E5E5',            # Subtle borders
            'success': '#107C10',           # Green
            'warning': '#F7630C',           # Orange
            'error': '#D13438',             # Red
            'nav_active': '#E8F3FF',        # Light blue for active nav
        }
        
        logger.debug(f"Color scheme initialized: {len(self.colors)} colors defined")
    
    @logged_method
    def show(self):
        """Show the settings window with modern Windows 11 design."""
        try:
            if self.window and self.window.winfo_exists():
                logger.info("Settings window already exists, bringing to front")
                self.window.lift()
                self.window.focus_force()
                return
            
            logger.info("Creating new settings window")
            self.window = tk.Tk()
            self.window.title("Settings - Phoenix Tracker")
            self.window.geometry("900x650")
            self.window.resizable(False, False)
            self.window.configure(bg=self.colors['bg_primary'])
            
            # Set window icon (if available)
            try:
                # Could add icon here
                pass
            except Exception as e:
                logger.warning(f"Could not set window icon: {e}")
            
            self._create_layout()
            self._load_settings()
            
            # Center window on screen
            self._center_window()
            
            logger.info("Settings window created successfully")
            self.window.mainloop()
            
        except Exception as e:
            log_exception(e, "Failed to show settings window")
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def _center_window(self):
        """Center the window on screen."""
        try:
            self.window.update_idletasks()
            x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
            y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
            self.window.geometry(f"+{x}+{y}")
            logger.debug(f"Window centered at position ({x}, {y})")
        except Exception as e:
            log_exception(e, "Failed to center window")
    
    @logged_method
    def _create_layout(self):
        """Create the main window layout with left navigation."""
        try:
            # Main container
            main_container = tk.Frame(self.window, bg=self.colors['bg_primary'])
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Left navigation pane (Windows 11 style)
            nav_frame = tk.Frame(
                main_container,
                bg=self.colors['card'],
                width=200
            )
            nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
            nav_frame.pack_propagate(False)
            
            # Header in nav
            header = tk.Label(
                nav_frame,
                text="Phoenix Tracker",
                font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
                bg=self.colors['card'],
                fg=self.colors['text_primary'],
                pady=20
            )
            header.pack(fill=tk.X, padx=15)
            
            # Navigation items
            self.nav_buttons = {}
            nav_items = [
                ("server", "🌐 Server", self._show_server_page),
                ("capture", "⏱️ Capture", self._show_capture_page),
                ("performance", "⚡ Performance", self._show_performance_page),
                ("security", "🔒 Security", self._show_security_page),
                ("token", "🔑 Token", self._show_token_page),
                ("advanced", "🔧 Advanced", self._show_advanced_page),
            ]
            
            for page_id, label, command in nav_items:
                btn = tk.Button(
                    nav_frame,
                    text=label,
                    command=command,
                    bg=self.colors['card'],
                    fg=self.colors['text_primary'],
                    font=tkfont.Font(family="Segoe UI", size=10),
                    relief=tk.FLAT,
                    anchor="w",
                    padx=20,
                    pady=12,
                    cursor="hand2",
                    activebackground=self.colors['nav_active']
                )
                btn.pack(fill=tk.X)
                self.nav_buttons[page_id] = btn
                
                # Add hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.colors['nav_active']))
                btn.bind("<Leave>", lambda e, b=btn, pid=page_id: b.configure(
                    bg=self.colors['nav_active'] if pid == self.current_page else self.colors['card']
                ))
            
            # Right content area
            self.content_frame = tk.Frame(
                main_container,
                bg=self.colors['bg_primary']
            )
            self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            # Bottom button bar
            button_bar = tk.Frame(
                self.content_frame,
                bg=self.colors['card'],
                height=70
            )
            button_bar.pack(side=tk.BOTTOM, fill=tk.X)
            button_bar.pack_propagate(False)
            
            # Save button (accent color)
            save_btn = tk.Button(
                button_bar,
                text="Save",
                command=self._save_settings,
                bg=self.colors['accent'],
                fg="white",
                font=tkfont.Font(family="Segoe UI", size=11, weight="bold"),
                relief=tk.FLAT,
                padx=40,
                pady=10,
                cursor="hand2",
                activebackground=self.colors['accent_hover']
            )
            save_btn.pack(side=tk.RIGHT, padx=20, pady=15)
            
            # Cancel button
            cancel_btn = tk.Button(
                button_bar,
                text="Cancel",
                command=self._cancel,
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=tkfont.Font(family="Segoe UI", size=11),
                relief=tk.FLAT,
                padx=30,
                pady=10,
                cursor="hand2"
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5, pady=15)
            
            # Create initial page
            self._show_server_page()
            
            logger.debug("Layout created successfully")
            
        except Exception as e:
            log_exception(e, "Failed to create layout")
            raise
    
    def _set_active_nav(self, page_id: str):
        """Highlight the active navigation item."""
        try:
            self.current_page = page_id
            for pid, btn in self.nav_buttons.items():
                if pid == page_id:
                    btn.configure(bg=self.colors['nav_active'], font=tkfont.Font(family="Segoe UI", size=10, weight="bold"))
                else:
                    btn.configure(bg=self.colors['card'], font=tkfont.Font(family="Segoe UI", size=10))
            logger.debug(f"Active navigation set to: {page_id}")
        except Exception as e:
            log_exception(e, f"Failed to set active nav: {page_id}")
    
    def _clear_content(self):
        """Clear the content area."""
        try:
            for widget in self.content_frame.winfo_children():
                if not isinstance(widget, tk.Frame) or widget.winfo_height() != 70:  # Don't remove button bar
                    widget.destroy()
            logger.debug("Content area cleared")
        except Exception as e:
            log_exception(e, "Failed to clear content")
    
    def _create_page_header(self, parent, title: str, subtitle: str = ""):
        """Create a modern page header with hero control."""
        try:
            header_frame = tk.Frame(parent, bg=self.colors['card'])
            header_frame.pack(fill=tk.X, padx=25, pady=(25, 15))
            
            # Title
            title_label = tk.Label(
                header_frame,
                text=title,
                font=tkfont.Font(family="Segoe UI", size=20, weight="bold"),
                bg=self.colors['card'],
                fg=self.colors['text_primary']
            )
            title_label.pack(anchor="w")
            
            # Subtitle if provided
            if subtitle:
                subtitle_label = tk.Label(
                    header_frame,
                    text=subtitle,
                    font=tkfont.Font(family="Segoe UI", size=10),
                    bg=self.colors['card'],
                    fg=self.colors['text_secondary']
                )
                subtitle_label.pack(anchor="w", pady=(5, 0))
            
            logger.debug(f"Page header created: {title}")
        except Exception as e:
            log_exception(e, f"Failed to create page header: {title}")
    
    def _create_setting_card(self, parent, title: str) -> tk.Frame:
        """Create a modern card for settings group."""
        try:
            card = tk.Frame(
                parent,
                bg=self.colors['card'],
                highlightbackground=self.colors['border'],
                highlightthickness=1
            )
            card.pack(fill=tk.X, padx=25, pady=10)
            
            # Card title
            title_label = tk.Label(
                card,
                text=title,
                font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
                bg=self.colors['card'],
                fg=self.colors['text_primary']
            )
            title_label.pack(anchor="w", padx=20, pady=(15, 10))
            
            logger.debug(f"Setting card created: {title}")
            return card
        except Exception as e:
            log_exception(e, f"Failed to create setting card: {title}")
            return tk.Frame(parent)
    
    def _create_text_field(self, parent, label: str, field_name: str, placeholder: str = ""):
        """Create a modern text input field."""
        try:
            row = tk.Frame(parent, bg=self.colors['card'])
            row.pack(fill=tk.X, padx=20, pady=8)
            
            # Label
            label_widget = tk.Label(
                row,
                text=label,
                font=tkfont.Font(family="Segoe UI", size=10),
                bg=self.colors['card'],
                fg=self.colors['text_primary'],
                anchor="w"
            )
            label_widget.pack(anchor="w", pady=(0, 5))
            
            # Entry
            entry = tk.Entry(
                row,
                font=tkfont.Font(family="Segoe UI", size=10),
                relief=tk.SOLID,
                borderwidth=1,
                highlightthickness=1,
                highlightcolor=self.colors['accent'],
                highlightbackground=self.colors['border']
            )
            entry.pack(fill=tk.X, ipady=6)
            
            if not hasattr(self, 'entries'):
                self.entries = {}
            self.entries[field_name] = entry
            
            logger.debug(f"Text field created: {field_name}")
        except Exception as e:
            log_exception(e, f"Failed to create text field: {field_name}")
    
    def _create_checkbox(self, parent, label: str, field_name: str):
        """Create a modern checkbox."""
        try:
            row = tk.Frame(parent, bg=self.colors['card'])
            row.pack(fill=tk.X, padx=20, pady=8)
            
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                row,
                text=label,
                variable=var,
                font=tkfont.Font(family="Segoe UI", size=10),
                bg=self.colors['card'],
                fg=self.colors['text_primary'],
                activebackground=self.colors['card'],
                selectcolor=self.colors['card']
            )
            checkbox.pack(anchor="w")
            
            if not hasattr(self, 'checkboxes'):
                self.checkboxes = {}
            self.checkboxes[field_name] = var
            
            logger.debug(f"Checkbox created: {field_name}")
        except Exception as e:
            log_exception(e, f"Failed to create checkbox: {field_name}")
    
    def _create_dropdown(self, parent, label: str, field_name: str, options: list):
        """Create a modern dropdown."""
        try:
            row = tk.Frame(parent, bg=self.colors['card'])
            row.pack(fill=tk.X, padx=20, pady=8)
            
            # Label
            label_widget = tk.Label(
                row,
                text=label,
                font=tkfont.Font(family="Segoe UI", size=10),
                bg=self.colors['card'],
                fg=self.colors['text_primary'],
                anchor="w"
            )
            label_widget.pack(anchor="w", pady=(0, 5))
            
            # Dropdown
            var = tk.StringVar()
            dropdown = ttk.Combobox(
                row,
                textvariable=var,
                values=options,
                state="readonly",
                font=tkfont.Font(family="Segoe UI", size=10)
            )
            dropdown.pack(fill=tk.X, ipady=4)
            
            if not hasattr(self, 'dropdowns'):
                self.dropdowns = {}
            self.dropdowns[field_name] = var
            
            logger.debug(f"Dropdown created: {field_name}")
        except Exception as e:
            log_exception(e, f"Failed to create dropdown: {field_name}")
    
    # Page creation methods
    @logged_method
    def _show_server_page(self):
        """Show server configuration page."""
        try:
            self._clear_content()
            self._set_active_nav("server")
            
            self._create_page_header(
                self.content_frame,
                "Server Configuration",
                "Configure your Phoenix server connection"
            )
            
            # Server settings card
            card = self._create_setting_card(self.content_frame, "Connection")
            self._create_text_field(card, "Phoenix API URL", "url", "https://phoenix.example.com")
            self._create_text_field(card, "Device ID", "device_id", self._get_default_device_id())
            
            # Add spacing at bottom
            tk.Frame(card, bg=self.colors['card'], height=15).pack()
            
        except Exception as e:
            log_exception(e, "Failed to show server page")
    
    @logged_method
    def _show_capture_page(self):
        """Show capture settings page."""
        try:
            self._clear_content()
            self._set_active_nav("capture")
            
            self._create_page_header(
                self.content_frame,
                "Capture Settings",
                "Control how often data is captured"
            )
            
            card = self._create_setting_card(self.content_frame, "Intervals")
            self._create_text_field(card, "Capture Interval (seconds)", "capture_interval", "60")
            self._create_text_field(card, "Heartbeat Interval (seconds)", "heartbeat_interval", "60")
            self._create_text_field(card, "Similarity Threshold (0-1)", "similarity_threshold", "0.95")
            
            tk.Frame(card, bg=self.colors['card'], height=15).pack()
            
        except Exception as e:
            log_exception(e, "Failed to show capture page")
    
    @logged_method
    def _show_performance_page(self):
        """Show performance settings page."""
        try:
            self._clear_content()
            self._set_active_nav("performance")
            
            self._create_page_header(
                self.content_frame,
                "Performance",
                "Adjust quality and resource usage"
            )
            
            card = self._create_setting_card(self.content_frame, "Image Quality")
            self._create_text_field(card, "Maximum Image Width (pixels)", "max_image_width", "1024")
            self._create_text_field(card, "JPEG Quality (1-100)", "jpeg_quality", "70")
            
            tk.Frame(card, bg=self.colors['card'], height=15).pack()
            
        except Exception as e:
            log_exception(e, "Failed to show performance page")
    
    @logged_method
    def _show_security_page(self):
        """Show security settings page."""
        try:
            self._clear_content()
            self._set_active_nav("security")
            
            self._create_page_header(
                self.content_frame,
                "Security",
                "Manage security and privacy settings"
            )
            
            card = self._create_setting_card(self.content_frame, "SSL/TLS")
            self._create_checkbox(card, "Verify SSL Certificates", "verify_ssl")
            
            tk.Frame(card, bg=self.colors['card'], height=15).pack()
            
        except Exception as e:
            log_exception(e, "Failed to show security page")
    
    @logged_method
    def _show_token_page(self):
        """Show token management page."""
        try:
            self._clear_content()
            self._set_active_nav("token")
            
            self._create_page_header(
                self.content_frame,
                "Authentication",
                "Manage your device token"
            )
            
            card = self._create_setting_card(self.content_frame, "Device Token")
            
            # Token status
            has_token = self.token_manager.get_token() is not None
            status_frame = tk.Frame(card, bg=self.colors['card'])
            status_frame.pack(fill=tk.X, padx=20, pady=10)
            
            status_text = "✅ Token configured" if has_token else "⚠️ No token configured"
            status_color = self.colors['success'] if has_token else self.colors['warning']
            
            status_label = tk.Label(
                status_frame,
                text=status_text,
                font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
                bg=self.colors['card'],
                fg=status_color
            )
            status_label.pack(anchor="w")
            
            # Buttons
            btn_frame = tk.Frame(card, bg=self.colors['card'])
            btn_frame.pack(fill=tk.X, padx=20, pady=15)
            
            setup_btn = tk.Button(
                btn_frame,
                text="Setup Token",
                command=self._setup_token,
                bg=self.colors['accent'],
                fg="white",
                font=tkfont.Font(family="Segoe UI", size=10),
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2"
            )
            setup_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            if has_token:
                delete_btn = tk.Button(
                    btn_frame,
                    text="Delete Token",
                    command=self._delete_token,
                    bg=self.colors['error'],
                    fg="white",
                    font=tkfont.Font(family="Segoe UI", size=10),
                    relief=tk.FLAT,
                    padx=20,
                    pady=8,
                    cursor="hand2"
                )
                delete_btn.pack(side=tk.LEFT)
            
        except Exception as e:
            log_exception(e, "Failed to show token page")
    
    @logged_method
    def _show_advanced_page(self):
        """Show advanced settings page."""
        try:
            self._clear_content()
            self._set_active_nav("advanced")
            
            self._create_page_header(
                self.content_frame,
                "Advanced",
                "Advanced configuration options"
            )
            
            card = self._create_setting_card(self.content_frame, "Logging")
            self._create_dropdown(card, "Log Level", "log_level", ["DEBUG", "INFO", "WARNING", "ERROR"])
            
            tk.Frame(card, bg=self.colors['card'], height=15).pack()
            
        except Exception as e:
            log_exception(e, "Failed to show advanced page")
    
    @logged_method
    def _load_settings(self):
        """Load settings from Windows Registry."""
        try:
            logger.info("Loading settings from Windows Registry")
            
            if hasattr(self, 'entries'):
                # Server settings
                if 'url' in self.entries:
                    url = settings_manager.get_phoenix_url()
                    if url:
                        self.entries['url'].delete(0, tk.END)
                        self.entries['url'].insert(0, url)
                        logger.debug(f"Loaded URL: {url}")
                
                if 'device_id' in self.entries:
                    device_id = settings_manager.get_device_id()
                    if device_id:
                        self.entries['device_id'].delete(0, tk.END)
                        self.entries['device_id'].insert(0, device_id)
                        logger.debug(f"Loaded device_id: {device_id}")
                
                # Capture settings
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
                
                # Performance settings
                if 'max_image_width' in self.entries:
                    width = settings_manager.get_setting('max_image_width', 1024)
                    self.entries['max_image_width'].delete(0, tk.END)
                    self.entries['max_image_width'].insert(0, str(width))
                
                if 'jpeg_quality' in self.entries:
                    quality = settings_manager.get_setting('jpeg_quality', 70)
                    self.entries['jpeg_quality'].delete(0, tk.END)
                    self.entries['jpeg_quality'].insert(0, str(quality))
            
            # Security settings
            if hasattr(self, 'checkboxes') and 'verify_ssl' in self.checkboxes:
                verify = settings_manager.get_verify_ssl()
                self.checkboxes['verify_ssl'].set(verify)
            
            # Advanced settings
            if hasattr(self, 'dropdowns') and 'log_level' in self.dropdowns:
                level = settings_manager.get_log_level()
                self.dropdowns['log_level'].set(level)
            
            logger.info("Settings loaded successfully")
            
        except Exception as e:
            log_exception(e, "Failed to load settings")
    
    @logged_method
    def _save_settings(self):
        """Save settings to Windows Registry."""
        try:
            logger.info("Saving settings to Windows Registry")
            
            # Validate and save URL
            if 'url' in self.entries:
                url = self.entries['url'].get().strip()
                if not url:
                    logger.warning("Validation failed: URL is empty")
                    messagebox.showerror("Error", "Phoenix API URL is required")
                    return
                
                if not url.startswith('https://') and not url.startswith('http://localhost'):
                    logger.warning(f"Validation failed: URL must use HTTPS: {url}")
                    messagebox.showerror("Error", "URL must use HTTPS (or http://localhost for testing)")
                    return
                
                settings_manager.save_phoenix_url(url)
                logger.info(f"Saved URL: {url}")
            
            # Validate and save Device ID
            if 'device_id' in self.entries:
                device_id = self.entries['device_id'].get().strip()
                if not device_id or len(device_id) < 3:
                    logger.warning("Validation failed: Device ID too short")
                    messagebox.showerror("Error", "Device ID must be at least 3 characters")
                    return
                
                settings_manager.save_device_id(device_id)
                logger.info(f"Saved device_id: {device_id}")
            
            # Save intervals
            if 'capture_interval' in self.entries:
                try:
                    capture_interval = int(self.entries['capture_interval'].get())
                    if capture_interval < 10:
                        raise ValueError("Capture interval must be at least 10 seconds")
                    settings_manager.save_capture_interval(capture_interval)
                    logger.info(f"Saved capture_interval: {capture_interval}")
                except ValueError as e:
                    logger.error(f"Invalid capture interval: {e}")
                    messagebox.showerror("Error", f"Invalid interval: {e}")
                    return
            
            if 'heartbeat_interval' in self.entries:
                try:
                    heartbeat_interval = int(self.entries['heartbeat_interval'].get())
                    if heartbeat_interval < 10:
                        raise ValueError("Heartbeat interval must be at least 10 seconds")
                    settings_manager.save_heartbeat_interval(heartbeat_interval)
                    logger.info(f"Saved heartbeat_interval: {heartbeat_interval}")
                except ValueError as e:
                    logger.error(f"Invalid heartbeat interval: {e}")
                    messagebox.showerror("Error", f"Invalid interval: {e}")
                    return
            
            # Save similarity threshold
            if 'similarity_threshold' in self.entries:
                try:
                    threshold = float(self.entries['similarity_threshold'].get())
                    if not 0 <= threshold <= 1:
                        raise ValueError("Similarity threshold must be between 0 and 1")
                    settings_manager.save_similarity_threshold(threshold)
                    logger.info(f"Saved similarity_threshold: {threshold}")
                except ValueError as e:
                    logger.error(f"Invalid similarity threshold: {e}")
                    messagebox.showerror("Error", f"Invalid similarity threshold: {e}")
                    return
            
            # Save performance settings
            if 'max_image_width' in self.entries:
                try:
                    max_width = int(self.entries['max_image_width'].get())
                    if max_width < 100:
                        raise ValueError("Image width must be at least 100 pixels")
                    settings_manager.save_setting('max_image_width', max_width)
                    logger.info(f"Saved max_image_width: {max_width}")
                except ValueError as e:
                    logger.error(f"Invalid image width: {e}")
                    messagebox.showerror("Error", f"Invalid performance setting: {e}")
                    return
            
            if 'jpeg_quality' in self.entries:
                try:
                    jpeg_quality = int(self.entries['jpeg_quality'].get())
                    if not 1 <= jpeg_quality <= 100:
                        raise ValueError("JPEG quality must be between 1 and 100")
                    settings_manager.save_setting('jpeg_quality', jpeg_quality)
                    logger.info(f"Saved jpeg_quality: {jpeg_quality}")
                except ValueError as e:
                    logger.error(f"Invalid JPEG quality: {e}")
                    messagebox.showerror("Error", f"Invalid performance setting: {e}")
                    return
            
            # Save checkboxes
            if hasattr(self, 'checkboxes') and 'verify_ssl' in self.checkboxes:
                verify = self.checkboxes['verify_ssl'].get()
                settings_manager.save_verify_ssl(verify)
                logger.info(f"Saved verify_ssl: {verify}")
            
            # Save dropdowns
            if hasattr(self, 'dropdowns') and 'log_level' in self.dropdowns:
                level = self.dropdowns['log_level'].get()
                settings_manager.save_log_level(level)
                logger.info(f"Saved log_level: {level}")
            
            logger.info("All settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")
            
            # Call callback
            if self.on_save:
                try:
                    self.on_save()
                    logger.debug("Save callback executed")
                except Exception as e:
                    log_exception(e, "Error in save callback")
            
            self.window.destroy()
            
        except Exception as e:
            log_exception(e, "Failed to save settings")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    @logged_method
    def _setup_token(self):
        """Setup authentication token."""
        try:
            logger.info("Opening token setup dialog")
            token = tk.simpledialog.askstring(
                "Setup Token",
                "Enter your device token from Phoenix Dashboard:",
                parent=self.window
            )
            
            if token:
                logger.info("Token provided, saving...")
                if self.token_manager.save_token(token.strip()):
                    logger.info("Token saved successfully")
                    messagebox.showinfo("Success", "Token saved successfully!")
                    # Refresh page
                    self._show_token_page()
                else:
                    logger.error("Failed to save token")
                    messagebox.showerror("Error", "Failed to save token")
            else:
                logger.info("Token setup cancelled by user")
                
        except Exception as e:
            log_exception(e, "Failed to setup token")
            messagebox.showerror("Error", f"Failed to setup token: {e}")
    
    @logged_method
    def _delete_token(self):
        """Delete authentication token."""
        try:
            logger.info("Token deletion requested")
            if messagebox.askyesno("Confirm", "Are you sure you want to delete the token?"):
                logger.info("User confirmed token deletion")
                if self.token_manager.delete_token():
                    logger.info("Token deleted successfully")
                    messagebox.showinfo("Success", "Token deleted successfully!")
                    # Refresh page
                    self._show_token_page()
                else:
                    logger.error("Failed to delete token")
                    messagebox.showerror("Error", "Failed to delete token")
            else:
                logger.info("Token deletion cancelled by user")
                
        except Exception as e:
            log_exception(e, "Failed to delete token")
            messagebox.showerror("Error", f"Failed to delete token: {e}")
    
    @logged_method
    def _cancel(self):
        """Cancel and close window."""
        logger.info("Settings window cancelled by user")
        self.window.destroy()
    
    def _get_default_device_id(self) -> str:
        """Get default device ID based on hostname."""
        try:
            hostname = socket.gethostname().lower()
            hostname = ''.join(c if c.isalnum() or c == '-' else '-' for c in hostname)
            device_id = f"desktop-{hostname}"
            logger.debug(f"Generated default device ID: {device_id}")
            return device_id
        except Exception as e:
            log_exception(e, "Failed to generate default device ID")
            return "desktop-unknown"


# Import simpledialog
import tkinter.simpledialog


if __name__ == "__main__":
    logger.info("Starting Modern Settings Window (standalone mode)")
    settings = ModernSettingsWindow()
    settings.show()
