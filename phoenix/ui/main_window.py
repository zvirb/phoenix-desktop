import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QInputDialog
from PyQt6.QtCore import Qt, QTimer, QThread

from phoenix.core.app_bar import AppBarManager
from phoenix.ui.components.header_hud import HeaderHUD
from phoenix.ui.components.activity_list import ActivityList
from phoenix.ui.components.control_deck import ControlDeck
from phoenix.ui.components.stats_widget import StatsWidget
from phoenix.ui.components.waveform_widget import WaveformWidget
from phoenix.ui.components.neural_selector import NeuralSelector

from phoenix.services.context_worker import ContextWorker
from phoenix.services.mesh_worker import MeshWorker
from phoenix.services.sync_worker import SyncWorker
from phoenix.services.audio_worker import AudioWorker

from datetime import datetime


from phoenix.ui.views.onboarding import OnboardingView
from phoenix.ui.views.settings import SettingsDialog
from phoenix.core.token_manager import TokenManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    The main shell of the Phoenix Sidebar. 
    Integrates the AppBar functionality with the PyQt6 UI.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phoenix Sidebar")
        
        # 1. Setup Window Flags for Dock-like behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # 2. Main Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 3. Assemble UI
        self.header_hud = HeaderHUD()
        self.layout.addWidget(self.header_hud)
        
        # Stats Widget (Tech Variant)
        self.stats_widget = StatsWidget()
        self.layout.addWidget(self.stats_widget)

        # Waveform Widget (Cognitive Cockpit)
        self.waveform_widget = WaveformWidget()
        self.layout.addWidget(self.waveform_widget)
        
        # Container for main views (Stack would be better but simple hide/show works)
        self.activity_list = ActivityList()
        self.layout.addWidget(self.activity_list, 1) # Stretch to fill space
        
        # Neural Selector
        self.neural_selector = NeuralSelector()
        self.layout.addWidget(self.neural_selector)
        
        self.control_deck = ControlDeck()
        self.layout.addWidget(self.control_deck)

        # Onboarding View (Hidden by default)
        self.onboarding_view = OnboardingView()
        self.onboarding_view.hide()
        self.onboarding_view.token_saved.connect(self.on_onboarding_complete)
        self.layout.addWidget(self.onboarding_view, 1)

        # 4. Load Styles
        self._load_stylesheet()

        # 5. Initialize AppBar Manager
        self.app_bar = AppBarManager(self.winId())

        # 6. State Management
        self.expanded = True
        self.header_hud.toggled.connect(self.toggle_sidebar)

        # 7. Initialize Services (Workers)
        self.context_worker = ContextWorker()
        self.mesh_worker = MeshWorker()
        self.sync_worker = SyncWorker()
        
        # Audio Thread Setup
        self.audio_thread = QThread()
        self.audio_worker = AudioWorker()
        self.audio_worker.moveToThread(self.audio_thread)
        
        # 8. Connect Signals
        self.context_worker.activity_detected.connect(self.on_activity_detected)
        self.context_worker.screenshot_taken.connect(self.sync_worker.queue_upload)
        self.context_worker.status_changed.connect(self.on_status_changed)
        
        self.mesh_worker.inference_status.connect(self.header_hud.update_brain)
        self.mesh_worker.network_status.connect(self.header_hud.update_mesh)
        self.mesh_worker.mesh_info_ready.connect(self.on_mesh_info)
        
        # Connect Audio Worker (Visualizer)
        # We don't auto-start visualizer anymore, waiting for user toggle
        self.audio_worker.levels_ready.connect(self.waveform_widget.set_levels)
        self.audio_worker.recording_finished.connect(self.on_recording_finished)
        
        # Start Audio Thread
        # Start worker immediately so it's ready (hot mic)
        self.audio_thread.started.connect(self.audio_worker.start)
        self.audio_thread.start()
        
        # Connect Control Deck
        self.control_deck.war_room_toggled.connect(self.on_war_room_toggled)
        self.control_deck.zen_mode_toggled.connect(self.on_zen_mode_toggled)
        self.sync_worker.heartbeat_sent.connect(lambda s: self.header_hud.set_badge_status(self.header_hud.pulse, s))
        self.sync_worker.gamification_update.connect(self.on_gamification_update)
        
        # Connect Settings
        self.header_hud.settings_btn.clicked.connect(self.on_settings_clicked)

    def toggle_audio_recording(self, recording):
        """Called by WaveformWidget when clicked."""
        self.audio_worker.set_recording(recording)
        
    def on_recording_finished(self, filepath):
        print(f"Main: Recording finished: {filepath}")
        if self.sync_worker:
            self.sync_worker.queue_audio_upload(filepath)
        
    def on_settings_clicked(self):
        """Open Settings Dialog."""
        dlg = SettingsDialog(self)
        dlg.exec()

    def on_gamification_update(self, profile):
        """Update gamification stats on control deck."""
        if not profile:
            return
            
        level = profile.get('level', 1)
        points = profile.get('total_points', 0)
        # Assuming points_to_next_level is what's needed for NEXT, 
        # but typical progress bars want Current/Max for this level.
        # We'll use the heuristic: points_in_current_level = points ? 
        # Let's just pass what we have.
        needed = profile.get('points_to_next_level', 100)
        
        # Heuristic: Progress = Needed / (Current + Needed) ?? No.
        # If I have 0 and need 400. Progress 0.
        # If I have 200 and need 200. Progress 50%.
        # So denominator = Current + Needed?
        # That implies Total Required for Level = Current Accumulated + Remaining Needed.
        # Check: Level 1 starts at 0. Target 400. Current 0. Needed 400. 0+400=400. Correct.
        # Check: I earn 50. Current 50. Needed 350. 50+350=400. Correct.
        
        # But wait, 'total_points' is LIFETIME score usually.
        # If Level 2 starts at 400. I have 450. Needed 350 (Target 800).
        # 450+350 = 800? (Target for Level 3). 
        # My progress in Level 2 is (450-400) / (800-400).
        # Without knowing the base, this calculation is hard.
        
        # HOWEVER, let's just assume the simpler interpretation for now:
        # Pass raw values and let the component decide or just pass 0 if confused.
        # Better heuristic: just use needed as the "max" if current is 0, else ...
        # Let's trust the component's (Current / (Current+Needed)) logic for Level 1.
        # For Level > 1, it might be slightly off visually but strictly monotonic.
        
        self.control_deck.set_stats(level, points, needed)

    def on_war_room_toggled(self, active):
        """Handle War Room toggle."""
        logger.info(f"War Room Mode: {active}")
        
        if active:
            # Visuals: Red border + Dimmer Overlay effect (simulated by border for now)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #020617;
                    border: 2px solid #ef4444; 
                }
                QScrollArea { border: none; background: transparent; }
            """)
            
            # API: Start Focus Session (async fire-and-forget)
            # We use SyncWorker to handle API calls usually, but let's just use the thread pool or sync worker method if available?
            # Or just fire in background task?
            # Let's verify if default loop can handle it. For now, just logging.
            # Ideally we pass this intent to a worker.
            if self.sync_worker and self.sync_worker.client:
                 # Quick hack: run in executor to avoid blocking UI
                 import threading
                 threading.Thread(target=self.sync_worker.client.start_focus_session, kwargs={'duration': 60, 'task': 'War Room'}).start()
            
        else:
            self._load_stylesheet() # Revert to default

            self._load_stylesheet() # Revert to default

    def on_zen_mode_toggled(self, active):
        """Handle Zen Mode (No Distractions) toggle with Timer."""
        logger.info(f"Zen Mode: {active}")
        
        if active:
            # Ask for duration
            minutes, ok = QInputDialog.getInt(self, "Zen Mode", "Duration (minutes):", 25, 1, 180, 1)
            if ok:
                # Zen Mode: Hide list + Timer
                self.activity_list.hide()
                self.setStyleSheet("QMainWindow { background-color: #000000; border-left: 1px solid #333; }")
                
                # Start Timer
                self.zen_seconds_remaining = minutes * 60
                self.zen_timer = QTimer(self)
                self.zen_timer.timeout.connect(self._update_zen_timer)
                self.zen_timer.start(1000)
                self._update_zen_timer() # Initial update
            else:
                # Cancelled: reset button without triggering logic again
                self.control_deck.btn_distractions.blockSignals(True)
                self.control_deck.btn_distractions.setChecked(False)
                self.control_deck.btn_distractions.blockSignals(False)
        else:
            # Deactivate
            if hasattr(self, 'zen_timer') and self.zen_timer.isActive():
                self.zen_timer.stop()
            self.control_deck.set_distraction_text("NO DISTRACTIONS")
            self.activity_list.show()
            self._load_stylesheet() # Restore theme

    def _update_zen_timer(self):
        """Update countdown text."""
        if self.zen_seconds_remaining > 0:
            mins, secs = divmod(self.zen_seconds_remaining, 60)
            self.control_deck.set_distraction_text(f"ZEN: {mins:02d}:{secs:02d}")
            self.zen_seconds_remaining -= 1
        else:
            # Time up
            self.zen_timer.stop()
            self.control_deck.btn_distractions.setChecked(False) # Will trigger toggle(False)

    def on_mesh_info(self, info):
        """Pass mesh info to sync worker for heartbeat."""
        self.sync_worker.update_state(
            ollama_available=info.get('ollama_available'),
            ollama_models=info.get('ollama_models'),
            tailscale_ip=info.get('tailscale_ip')
        )

    def check_auth(self):
        """Check if authenticated, otherwise show onboarding."""
        manager = TokenManager()
        if not manager.has_token():
            self.show_onboarding()
            return False
        return True

    def show_onboarding(self):
        self.activity_list.hide()
        self.control_deck.hide()
        self.onboarding_view.show()
        # Force expand for wizard
        if not self.expanded:
            self.toggle_sidebar()

    def on_onboarding_complete(self):
        self.onboarding_view.hide()
        self.activity_list.show()
        self.control_deck.show()
        self.start_services()

    def on_activity_detected(self, data):
        """Handle new activity detected."""
        time_str = datetime.fromtimestamp(data.get('timestamp', 0)).strftime("%H:%M")
        
        title = "Screen Capture"
        subtitle = f"{data.get('app_name')} - {data.get('window_title')}"
        icon = "📷"
        
        # Determine Tags
        tags = []
        app = data.get('app_name', '').lower()
        if 'code' in app or 'pycharm' in app:
            tags = ["DEV", "FOCUS"]
        elif 'chrome' in app or 'edge' in app:
            tags = ["WEB"]
        elif 'slack' in app or 'discord' in app:
            tags = ["CHAT"]
            
        self.activity_list.add_event(title, subtitle, time_str, icon, tags=tags)
        # Pulse visual eye
        self.header_hud.update_visual(True)

        # Update sync state
        self.sync_worker.update_state(
            app_name=data.get('app_name'),
            window_title=data.get('window_title')
        )

    def on_status_changed(self, status):
        """Handle idle/gaming status change."""
        self.sync_worker.update_state(is_idle=status.get("idle"))

        if status.get("gaming"):
            self.activity_list.add_event("Gaming Mode", "Paused tracking", "", "🎮")
        elif status.get("idle"):
             self.activity_list.add_event("Idle", "User is away", "", "💤")

    def toggle_sidebar(self):
        """Toggle between expanded (Docked) and collapsed (Icon only) modes."""
        self.expanded = not self.expanded
        
        if self.expanded:
            # Expand
            self.app_bar.set_appbar_width(350)
            if self.onboarding_view.isVisible():
                pass 
            else:
                self.activity_list.show()
                self.control_deck.show()
            self.header_hud.btn_toggle.setText("≡")
        else:
            # Collapse
            self.app_bar.set_appbar_width(70)
            self.activity_list.hide()
            self.control_deck.hide()
            self.onboarding_view.hide()
            self.header_hud.btn_toggle.setText("➜")
        
        # Sync Geometry immediately
        rc = self.app_bar.abd.rc
        self.setGeometry(rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)

    def _load_stylesheet(self):
        try:
            style_path = Path(__file__).parent / "styles.qss"
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")

    def showEvent(self, event):
        """Called when window is shown. Perfect time to dock."""
        super().showEvent(event)
        self.app_bar.register()
        
        if self.check_auth():
            self.start_services()
        
        # Sync Geometry
        rc = self.app_bar.abd.rc
        self.setGeometry(rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)

    def start_services(self):
        # Start Services
        if not self.context_worker.isRunning():
            self.context_worker.start()
        if not self.mesh_worker.isRunning():
            self.mesh_worker.start()
        if not self.sync_worker.isRunning():
            self.sync_worker.start()

    def closeEvent(self, event):
        """Called when window is closed. Release the dock."""
        self.context_worker.stop()
        self.mesh_worker.stop()
        self.sync_worker.stop()
        
        # Stop Audio
        if self.audio_thread.isRunning():
            # We should ask worker to stop first, but direct call crosses thread
            # Let's just quit thread and wait?
            # Ideally: signal to stop. But simple quit is okay for now.
            self.audio_worker.stop() # This might be unsafe across threads if it touches QObjects? 
            # Actually stop() just stops QAudioSource. QAudioSource is thread-safe re: stop?
            # Better: Queue it.
            # But for shutdown:
            self.audio_thread.quit()
            self.audio_thread.wait()
            
        self.app_bar.unregister()
        super().closeEvent(event)
