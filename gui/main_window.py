import customtkinter as ctk
import logging
from typing import Callable, Optional
import webbrowser
from PIL import Image
import os

from windows_settings import settings_manager
from settings_model import validate_settings
from phoenix.core.token_manager import TokenManager

logger = logging.getLogger(__name__)

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SettingsPage(ctk.CTkScrollableFrame):
    """Base class for settings pages."""
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        
        self.header = ctk.CTkLabel(
            self, 
            text=self.title, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header.pack(pady=20, padx=20, anchor="w")

    def add_section(self, title):
        label = ctk.CTkLabel(
            self, 
            text=title, 
            font=ctk.CTkFont(size=14, weight="bold", underline=False)
        )
        label.pack(pady=(20, 10), padx=20, anchor="w")
        return label

class ServerPage(SettingsPage):
    def __init__(self, master, state):
        super().__init__(master, "Server Configuration")
        self.form_data = state
        
        self.add_section("Connection")
        
        self.url_entry = self.add_input("Phoenix API URL", self.form_data['phoenix_url'])
        self.device_entry = self.add_input("Device ID", self.form_data['device_id'])
        
        self.add_section("Local Inference")
        self.ollama_entry = self.add_input("Ollama Port", self.form_data['ollama_port'])
        
        # Add a small note about the default port
        note = ctk.CTkLabel(
            self, 
            text="Note: Default port for Ollama updates is now 11450.",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        note.pack(pady=(0, 10), padx=20, anchor="w")
        
    def add_input(self, label_text, variable):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        label = ctk.CTkLabel(frame, text=label_text, width=150, anchor="w")
        label.pack(side="left")
        
        entry = ctk.CTkEntry(frame, textvariable=variable, width=300)
        entry.pack(side="left", expand=True, fill="x")
        return entry

class CapturePage(SettingsPage):
    def __init__(self, master, state):
        super().__init__(master, "Capture Settings")
        
        self.add_section("Timing")
        self.add_input("Capture Interval (sec)", state['capture_interval'])
        self.add_input("Heartbeat Interval (sec)", state['heartbeat_interval'])
        
        self.add_section("Detection")
        self.add_slider("Similarity Threshold", state['similarity_threshold'], 0.0, 1.0)
        
    def add_input(self, label_text, variable):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        label = ctk.CTkLabel(frame, text=label_text, width=200, anchor="w")
        label.pack(side="left")
        entry = ctk.CTkEntry(frame, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True)

    def add_slider(self, label_text, variable, min_val, max_val):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=10)
        
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x")
        
        label = ctk.CTkLabel(top_frame, text=label_text, anchor="w")
        label.pack(side="left")
        
        val_label = ctk.CTkLabel(top_frame, textvariable=variable, width=50, anchor="e")
        val_label.pack(side="right")
        
        slider = ctk.CTkSlider(
            frame, 
            from_=min_val, 
            to=max_val, 
            variable=variable,
        )
        slider.pack(fill="x", pady=5)

class TokenPage(SettingsPage):
    def __init__(self, master, token_manager):
        super().__init__(master, "Authentication")
        self.tm = token_manager
        
        self.status_var = ctk.StringVar(value="Checking...")
        
        # Create widgets FIRST
        self.status_label = ctk.CTkLabel(
            self, 
            textvariable=self.status_var,
            font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=20, padx=20, anchor="w")
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20)
        
        self.setup_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Setup New Token",
            command=self.setup_token
        )
        self.setup_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Delete Token",
            fg_color="red",
            hover_color="darkred",
            command=self.delete_token
        )
        # Don't pack delete_btn yet - update_status will handle it
        
        # NOW update status (after widgets exist)
        self.update_status()
        
    def update_status(self):
        token = self.tm.get_token()
        if token:
            self.status_var.set("✅ Token Configured")
            self.status_label.configure(text_color="green")
            self.delete_btn.pack(side="left", padx=5)
        else:
            self.status_var.set("⚠️ No Token Found")
            self.status_label.configure(text_color="orange")
            self.delete_btn.pack_forget()

    def setup_token(self):
        dialog = ctk.CTkInputDialog(text="Paste your device token from the dashboard:", title="Setup Token")
        token = dialog.get_input()
        if token:
            if self.tm.save_token(token.strip()):
                self.update_status()
            else:
                self.status_var.set("❌ Failed to save token")
    
    def delete_token(self):
        self.tm.delete_token()
        self.update_status()

class PerformancePage(SettingsPage):
    def __init__(self, master, form_data):
        super().__init__(master, "Performance Settings")
        self.form_data = form_data
        
        self.add_section("Image Quality")
        
        # Max image width
        frame1 = ctk.CTkFrame(self, fg_color="transparent")
        frame1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame1, text="Max Image Width (px)", width=200, anchor="w").pack(side="left")
        self.width_var = ctk.IntVar(value=1024)
        ctk.CTkEntry(frame1, textvariable=self.width_var, width=100).pack(side="left")
        
        # JPEG quality
        frame2 = ctk.CTkFrame(self, fg_color="transparent")
        frame2.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame2, text="JPEG Quality (1-100)", width=200, anchor="w").pack(side="left")
        self.quality_var = ctk.IntVar(value=70)
        ctk.CTkEntry(frame2, textvariable=self.quality_var, width=100).pack(side="left")
        
        self.add_section("Security")
        
        # SSL verification
        self.ssl_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Verify SSL Certificates", variable=self.ssl_var).pack(padx=20, pady=10, anchor="w")
        
        self.add_section("Logging")
        ctk.CTkLabel(self, text="Log Level: INFO (hardcoded for now)").pack(padx=20, anchor="w")


class ModernSettingsWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Phoenix Tracker Settings")
        self.geometry("800x600")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # State variables (linked to settings)
        self.init_state()
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Phoenix\nTracker", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(padx=20, pady=(20, 10))
        
        self.nav_buttons = []
        self.pages = {}
        
        self.create_nav_button("Server", self.show_server)
        self.create_nav_button("Capture", self.show_capture)
        self.create_nav_button("Performance", self.show_performance) # TODO
        self.create_nav_button("Token", self.show_token)
        
        # Save Button at bottom of sidebar
        self.save_btn = ctk.CTkButton(
            self.sidebar,
            text="Save Settings",
            command=self.save_settings,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.save_btn.pack(side="bottom", pady=20, padx=20)
        
        # Main Content Area
        self.current_frame = None
        
        # Initialize pages
        self.pages = {}
        
        # Show first page
        self.show_server()
        
    def init_state(self):
        self.form_data = {
            'phoenix_url': ctk.StringVar(value=settings_manager.get_phoenix_url() or "https://"),
            'device_id': ctk.StringVar(value=settings_manager.get_device_id() or ""),
            'capture_interval': ctk.IntVar(value=settings_manager.get_capture_interval()),
            'heartbeat_interval': ctk.IntVar(value=settings_manager.get_heartbeat_interval()),
            'similarity_threshold': ctk.DoubleVar(value=settings_manager.get_similarity_threshold()),
            'ollama_port': ctk.IntVar(value=settings_manager.get_ollama_port()),
        }
        
    def create_nav_button(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            command=command, 
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w"
        )
        btn.pack(fill="x", padx=10, pady=5)
        self.nav_buttons.append(btn)
        
    def show_frame(self, frame_class, *args):
        # Remove current frame
        if self.current_frame:
            self.current_frame.grid_forget()
            
        # Create page if needed
        if frame_class not in self.pages:
            self.pages[frame_class] = frame_class(self, *args)
            
        # Show new frame using grid (to match sidebar which uses grid)
        self.current_frame = self.pages[frame_class]
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_server(self):
        self.show_frame(ServerPage, self.form_data)

    def show_capture(self):
        self.show_frame(CapturePage, self.form_data)
        
    def show_performance(self):
        self.show_frame(PerformancePage, self.form_data)
        
    def show_token(self):
        self.show_frame(TokenPage, TokenManager())

    def save_settings(self):
        """Validate and save settings using Pydantic model."""
        data = {
            'phoenix_url': self.form_data['phoenix_url'].get(),
            'device_id': self.form_data['device_id'].get(),
            'capture_interval': self.form_data['capture_interval'].get(),
            'heartbeat_interval': self.form_data['heartbeat_interval'].get(),
            'similarity_threshold': self.form_data['similarity_threshold'].get(),
            'ollama_port': self.form_data['ollama_port'].get(),
            'max_image_width': 1024, # Defaults for now
            'jpeg_quality': 70,
            'verify_ssl': True,
            'log_level': 'INFO'
        }
        
        is_valid, error, model = validate_settings(data)
        
        if not is_valid:
            logger.error(f"Validation failed: {error}")
            # In a real app, show a message box
            # CTk doesn't have a built-in messagebox yet, usually use standard tkinter one
            import tkinter.messagebox
            tkinter.messagebox.showerror("Validation Error", error)
            return

        # Save to registry
        settings_manager.save_phoenix_url(model.phoenix_url)
        settings_manager.save_device_id(model.device_id)
        settings_manager.save_capture_interval(model.capture_interval)
        settings_manager.save_heartbeat_interval(model.heartbeat_interval)
        settings_manager.save_similarity_threshold(model.similarity_threshold)
        settings_manager.save_ollama_port(model.ollama_port)
        
        logger.info("Settings saved successfully!")
        import tkinter.messagebox
        tkinter.messagebox.showinfo("Success", "Settings saved successfully. Restart the tracker to apply changes.")

def main():
    app = ModernSettingsWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
