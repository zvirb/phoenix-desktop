"""
Gaming mode detection to pause tracking during gaming sessions.
"""
import logging
from typing import List
import psutil

from config import config

logger = logging.getLogger(__name__)


class GamingDetector:
    """Detect if user is in a gaming session."""
    
    def __init__(self, gaming_processes: List[str] = None):
        """
        Initialize gaming detector.
        
        Args:
            gaming_processes: List of process names to detect (case-insensitive)
        """
        self.gaming_processes = gaming_processes or config.GAMING_PROCESSES
        # Ensure all process names are lowercase for comparison
        self.gaming_processes = [p.lower() for p in self.gaming_processes]
    
    def is_gaming(self, active_process_name: str = None) -> bool:
        """
        Check if a gaming process is currently running.
        
        Args:
            active_process_name: Optional name of the currently active process.
                               If provided, only checks this process (much faster).

        Returns:
            True if gaming detected, False otherwise
        """
        try:
            # Fast path: Check active process if provided
            if active_process_name:
                if active_process_name.lower() in self.gaming_processes:
                    logger.info(f"Gaming detected (active window): {active_process_name}")
                    return True
                # If active process is known and not a game, assume not gaming
                # This skips the expensive full process scan
                return False

            # Slow path: Check all running processes
            for proc in psutil.process_iter(['name']):
                try:
                    process_name = proc.info['name'].lower()
                    if process_name in self.gaming_processes:
                        logger.info(f"Gaming detected: {proc.info['name']}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking gaming processes: {e}")
            return False
    
    def get_running_game(self, active_process_name: str = None) -> str:
        """
        Get the name of the currently running game, if any.
        
        Args:
            active_process_name: Optional name of the currently active process.

        Returns:
            Name of the game process, or empty string if none detected
        """
        try:
            # Fast path
            if active_process_name:
                if active_process_name.lower() in self.gaming_processes:
                    return active_process_name
                return ""

            # Slow path
            for proc in psutil.process_iter(['name']):
                try:
                    process_name = proc.info['name'].lower()
                    if process_name in self.gaming_processes:
                        return proc.info['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return ""
            
        except Exception as e:
            logger.error(f"Error getting game name: {e}")
            return ""
    
    def is_high_gpu_usage(self, threshold: float = 80.0) -> bool:
        """
        Check if GPU usage is high (indicates gaming or intensive graphics work).
        Note: This requires additional dependencies (gputil or nvidia-ml-py3)
        and is not implemented in this basic version.
        
        Args:
            threshold: GPU usage percentage threshold
            
        Returns:
            False (not implemented)
        """
        # This would require GPU monitoring libraries
        # For now, we only use process detection
        return False
    
    def add_process(self, process_name: str) -> None:
        """
        Add a process to the gaming blacklist.
        
        Args:
            process_name: Name of the process to add
        """
        process_name = process_name.lower()
        if process_name not in self.gaming_processes:
            self.gaming_processes.append(process_name)
            logger.info(f"Added {process_name} to gaming blacklist")
    
    def remove_process(self, process_name: str) -> None:
        """
        Remove a process from the gaming blacklist.
        
        Args:
            process_name: Name of the process to remove
        """
        process_name = process_name.lower()
        if process_name in self.gaming_processes:
            self.gaming_processes.remove(process_name)
            logger.info(f"Removed {process_name} from gaming blacklist")


# Convenience function
def is_gaming_active() -> bool:
    """Quick check if gaming is active."""
    detector = GamingDetector()
    return detector.is_gaming()


if __name__ == "__main__":
    # Test the gaming detector
    logging.basicConfig(level=logging.INFO)
    
    detector = GamingDetector()
    
    print(f"Gaming processes to detect: {detector.gaming_processes}")
    print(f"Gaming active: {detector.is_gaming()}")
    
    game = detector.get_running_game()
    if game:
        print(f"Currently playing: {game}")
    else:
        print("No gaming detected")
    
    # List all running processes (for debugging)
    print("\nAll running processes:")
    for proc in psutil.process_iter(['name']):
        try:
            print(f"  - {proc.info['name']}")
        except:
            pass
