"""
Data caching mechanism for Phoenix Tracker.
Stores failed uploads locally to be retried later.
"""
import sqlite3
import json
import logging
import time
import os
from typing import Dict, Any, Optional, List, Tuple

from phoenix_logging import get_logger, log_exception

logger = get_logger(__name__)

class DataCache:
    """
    Local cache for storing data when upload fails.
    Uses SQLite to persist data across restarts.
    """
    
    def __init__(self, db_path: str = "phoenix_cache.db"):
        """
        Initialize the data cache.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pending_uploads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        type TEXT NOT NULL,
                        data TEXT NOT NULL,
                        file_data BLOB
                    )
                """)
                conn.commit()
        except Exception as e:
            log_exception(e, "Failed to initialize cache database")
            
    def add_item(self, item_type: str, data: Dict[str, Any], file_data: Optional[bytes] = None) -> bool:
        """
        Add an item to the cache.
        
        Args:
            item_type: Type of item ('screenshot', 'heartbeat')
            data: Metadata dictionary
            file_data: Optional binary data (e.g., image bytes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO pending_uploads (timestamp, type, data, file_data) VALUES (?, ?, ?, ?)",
                    (time.time(), item_type, json.dumps(data), file_data)
                )
                conn.commit()
            logger.info(f"Cached {item_type} for later upload")
            return True
        except Exception as e:
            log_exception(e, "Failed to cache item")
            return False
            
    def get_pending_items(self, limit: int = 10) -> List[Tuple[int, str, Dict[str, Any], Optional[bytes]]]:
        """
        Get pending items from the cache.
        
        Args:
            limit: Maximum number of items to retrieve
            
        Returns:
            List of tuples (id, type, data, file_data)
        """
        items = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, type, data, file_data FROM pending_uploads ORDER BY timestamp ASC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                
                for row in rows:
                    item_id, item_type, data_json, file_data = row
                    try:
                        data = json.loads(data_json)
                        items.append((item_id, item_type, data, file_data))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode cached data for item {item_id}")
                        # Optionally delete corrupted item? For now, we'll skip it.
                        
        except Exception as e:
            log_exception(e, "Failed to retrieve pending items")
            
        return items
        
    def remove_item(self, item_id: int) -> bool:
        """
        Remove an item from the cache.
        
        Args:
            item_id: ID of the item to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pending_uploads WHERE id = ?", (item_id,))
                conn.commit()
            return True
        except Exception as e:
            log_exception(e, f"Failed to remove item {item_id}")
            return False
            
    def clear_cache(self) -> bool:
        """
        Clear all items from the cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pending_uploads")
                conn.commit()
            return True
        except Exception as e:
            log_exception(e, "Failed to clear cache")
            return False
            
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with 'count' and 'size_bytes' (approximate)
        """
        stats = {'count': 0, 'size_bytes': 0}
        try:
            if os.path.exists(self.db_path):
                stats['size_bytes'] = os.path.getsize(self.db_path)
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM pending_uploads")
                stats['count'] = cursor.fetchone()[0]
        except Exception as e:
            log_exception(e, "Failed to get cache stats")
            
        return stats
