import customtkinter as ctk
from token_manager import TokenManager
from api_client import create_client
from windows_settings import settings_manager
import logging
import threading

logger = logging.getLogger(__name__)

class SetupWizard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Phoenix Tracker Setup")
        self.geometry("600x400")
        
        self.token_manager = TokenManager()
        self.steps = [self.step_welcome, self.step_server, self.step_token, self.step_test, self.step_finish]
        self.current_step = 0
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.nav_frame = ctk.CTkFrame(self, height=50)
        self.nav_frame.pack(fill="x", side="bottom", padx=20, pady=20)
        
        self.back_btn = ctk.CTkButton(self.nav_frame, text="Back", command=self.go_back, state="disabled")
        self.back_btn.pack(side="left")
        
        self.next_btn = ctk.CTkButton(self.nav_frame, text="Next", command=self.go_next)
        self.next_btn.pack(side="right")
        
        # State
        self.url_var = ctk.StringVar(value="https://phoenix.example.com")
        self.device_id_var = ctk.StringVar(value=settings_manager.get_device_id() or "DEVICE-001")
        self.ollama_port_var = ctk.StringVar(value=str(settings_manager.get_ollama_port()))
        self.token_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="")
        
        self.show_step()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_step(self):
        self.clear_container()
        self.steps[self.current_step]()
        
        # Update buttons
        if self.current_step == 0:
            self.back_btn.configure(state="disabled")
        else:
            self.back_btn.configure(state="normal")
            
        if self.current_step == len(self.steps) - 1:
            self.next_btn.configure(text="Finish")
        else:
            self.next_btn.configure(text="Next")

    def go_next(self):
        if self.current_step == 1: # Server
            # Save server settings
            settings_manager.save_phoenix_url(self.url_var.get())
            settings_manager.save_device_id(self.device_id_var.get())
            try:
                settings_manager.save_ollama_port(int(self.ollama_port_var.get()))
            except ValueError:
                pass # Use default if invalid
            
        if self.current_step == 2: # Token
            if self.token_var.get():
                self.token_manager.save_token(self.token_var.get().strip())
        
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()
        else:
            self.destroy()

    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()

    def step_welcome(self):
        ctk.CTkLabel(self.container, text="Welcome to Phoenix Tracker", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.container, text="This wizard will help you set up your tracker.\n\nYou will need:\n1. The Phoenix Server URL\n2. A Device Token from the Dashboard", font=ctk.CTkFont(size=16)).pack(pady=20)

    def step_server(self):
        ctk.CTkLabel(self.container, text="Server Configuration", font=ctk.CTkFont(size=20)).pack(pady=10)
        
        ctk.CTkLabel(self.container, text="Phoenix Server URL:").pack(anchor="w")
        ctk.CTkEntry(self.container, textvariable=self.url_var, width=400).pack(pady=5)
        
        ctk.CTkLabel(self.container, text="Device ID:").pack(anchor="w")
        ctk.CTkEntry(self.container, textvariable=self.device_id_var, width=400).pack(pady=5)

        ctk.CTkLabel(self.container, text="Ollama Port (default 11450):").pack(anchor="w")
        ctk.CTkEntry(self.container, textvariable=self.ollama_port_var, width=400).pack(pady=5)

    def step_token(self):
        ctk.CTkLabel(self.container, text="Authentication", font=ctk.CTkFont(size=20)).pack(pady=10)
        ctk.CTkLabel(self.container, text="Paste your Device Token:").pack(anchor="w")
        entry = ctk.CTkEntry(self.container, textvariable=self.token_var, width=400, show="*")
        entry.pack(pady=5)
        
        ctk.CTkLabel(self.container, text="You can find this in the Phoenix Dashboard under Settings > Devices.").pack(pady=20)

    def step_test(self):
        ctk.CTkLabel(self.container, text="Connection Test", font=ctk.CTkFont(size=20)).pack(pady=10)
        
        status_label = ctk.CTkLabel(self.container, textvariable=self.status_var, font=ctk.CTkFont(size=16))
        status_label.pack(pady=20)
        
        def run_test():
            self.status_var.set("Testing connection...")
            client = create_client(self.url_var.get(), self.device_id_var.get())
            if not client:
                 self.status_var.set("❌ Internal Client Error")
                 return

            # Try to auth
            auth_res = client.authenticate(self.token_manager.get_token())
            if auth_res.get('status') != 'failed' and auth_res.get('access_token'):
                self.status_var.set("✅ Connection Successful!")
            else:
                 self.status_var.set(f"❌ Failed: {auth_res.get('error')}")

        ctk.CTkButton(self.container, text="Run Test", command=lambda: threading.Thread(target=run_test).start()).pack(pady=10)

    def step_finish(self):
        ctk.CTkLabel(self.container, text="Setup Complete!", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.container, text="The tracker is now ready to run in the background.").pack(pady=10)

def main():
    app = SetupWizard()
    app.mainloop()

if __name__ == "__main__":
    main()
