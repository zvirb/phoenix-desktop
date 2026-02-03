"""
Offline data queuing system using SQLite.
Stores failed API requests to be retried later when connectivity is restored.
"""
import sqlite3
import json
import logging
import os
from pathlib import Path
from datetime import datetime
import threading
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class RequestQueue:
    """Persistent queue for failed API requests."""
    
    def __init__(self, db_name: str = "phoenix_queue.db"):
        app_data = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "PhoenixTracker"
        app_data.mkdir(parents=True, exist_ok=True)
        self.db_path = app_data / db_name
        self._local = threading.local()
        self._init_db()
        
    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS request_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        data TEXT,  -- JSON payload
                        headers TEXT, -- JSON headers
                        files TEXT, -- JSON file metadata (limited support)
                        priority INTEGER DEFAULT 1,
                        retry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Optimize queue retrieval: Add index for priority and creation time
                conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_priority_created ON request_queue (priority DESC, created_at ASC)")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize queue DB: {e}")

    def add(self, endpoint: str, method: str, data: Optional[Dict] = None, 
            headers: Optional[Dict] = None, priority: int = 1) -> bool:
        """Add a request to the queue."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Serialize
            json_data = json.dumps(data) if data else None
            json_headers = json.dumps(headers) if headers else None

            cursor.execute("""
                INSERT INTO request_queue (endpoint, method, data, headers, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (endpoint, method, json_data, json_headers, priority))
            
            conn.commit()
            logger.info(f"Queued request to {endpoint} (Priority: {priority})")
            return True
        except Exception as e:
            logger.error(f"Failed to queue request: {e}")
            return False

    def peek(self, limit: int = 10) -> List[Dict]:
        """View pending requests without removing them."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM request_queue 
                ORDER BY priority DESC, created_at ASC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to peek queue: {e}")
            return []

    def pop(self, request_id: int):
        """Remove a request from the queue (after successful processing)."""
        try:
            conn = self._get_conn()
            conn.execute("DELETE FROM request_queue WHERE id = ?", (request_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to pop request {request_id}: {e}")

    def count(self) -> int:
        """Get usage stats."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM request_queue")
            return cursor.fetchone()[0]
        except Exception:
            return 0
