import sys
import logging
import asyncio
from qasync import QEventLoop
from PyQt6.QtWidgets import QApplication

from phoenix.ui.main_window import MainWindow

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from PyQt6.QtCore import QLockFile, QDir

def main():
    """Main Application Entry Point."""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("PhoenixSidebar")
        
        # Singleton Check using QLockFile
        # lock_file = QLockFile(QDir.tempPath() + "/phoenix_sidebar_v2.lock")
        # if not lock_file.tryLock(100):
        #     logger.warning("Phoenix Sidebar is already running. Exiting.")
        #     sys.exit(0)
        
        # Integrate asyncio with PyQt event loop
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        window = MainWindow()
        window.show()
        
        with loop:
            loop.run_forever()
            
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
