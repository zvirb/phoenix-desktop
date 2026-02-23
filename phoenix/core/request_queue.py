"""
Offline data queuing system using SQLite.
Stores failed API requests to be retried later when connectivity is restored.
Encryption added for sensitive data at rest.
"""
import sqlite3
import json
import logging
import os
import time
import base64
from pathlib import Path
from datetime import datetime
import threading
from typing import Optional, Dict, Any, List

try:
    import win32crypt
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class RequestQueue:
    """Persistent queue for failed API requests."""
    
    def __init__(self, db_name: str = "phoenix_queue.db"):
        app_data = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "PhoenixTracker"
        app_data.mkdir(parents=True, exist_ok=True)
        self.db_path = app_data / db_name
        self._local = threading.local()
        self._init_encryption()
        self._init_db()
        
    def _ensure_secure_permissions(self, file_path: Path) -> None:
        """
        Ensure file has strict permissions (0o600) on POSIX systems.
        Raises RuntimeError if permissions cannot be secured.
        """
        if not file_path.exists():
            return

        # Skip on Windows as chmod/stat behavior is different and we use DPAPI there normally
        if os.name == 'nt':
            return

        # 1. Try to set strict permissions (read/write for owner only)
        try:
            file_path.chmod(0o600)
        except Exception as e:
            # If chmod fails (e.g. not owner), we must check if it's already secure
            logger.warning(f"Failed to chmod {file_path}: {e}")

        # 2. Verify permissions
        try:
            # Check if group or others have any permissions
            # st_mode & 0o077 should be 0 for 0o600 (rw-------)
            # We explicitly want to forbid group/world access
            st = file_path.stat()
            if st.st_mode & 0o077:
                raise RuntimeError(
                    f"Insecure permissions on {file_path}: {oct(st.st_mode & 0o777)}. "
                    "File must be accessible only by owner (0o600)."
                )
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Failed to verify permissions on {file_path}: {e}")

    def _init_encryption(self):
        """Initialize encryption key for non-Windows platforms."""
        if not WINDOWS_AVAILABLE:
            self.key_file = Path.home() / ".phoenix_key"

            # Try to read existing key first
            if self.key_file.exists():
                try:
                    # Security: Ensure correct permissions
                    self._ensure_secure_permissions(self.key_file)
                except Exception as e:
                    logger.warning(f"Could not secure key file permissions: {e}")

                try:
                    self.encryption_key = self.key_file.read_bytes()
                    self.fernet = Fernet(self.encryption_key)
                    return
                except Exception:
                    pass # Fallback to generation if read fails

            # Generate new key and save atomically
            new_key = Fernet.generate_key()
            try:
                # Security: Atomic creation with 0600 permissions
                # O_EXCL ensures we don't overwrite if created concurrently
                fd = os.open(str(self.key_file), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                try:
                    os.write(fd, new_key)
                    self.encryption_key = new_key
                finally:
                    os.close(fd)
            except FileExistsError:
                # Race condition: file created by another process
                try:
                    # Wait for the other process to finish writing
                    for attempt in range(5):
                        try:
                            time.sleep(0.1)
                            key = self.key_file.read_bytes()
                            if key and len(key) > 0:
                                self.encryption_key = key
                                break
                        except Exception:
                            pass

                    # If still failing, try one last read
                    if not hasattr(self, 'encryption_key'):
                        self.encryption_key = self.key_file.read_bytes()
                except Exception as e:
                    logger.error(f"Failed to read existing encryption key: {e}")
                    # Fallback to memory-only key (persistence broken but app works for this session)
                    self.encryption_key = new_key

            except Exception as e:
                logger.error(f"Failed to save encryption key: {e}")
                # Fallback to memory-only key (persistence broken but app works for this session)
                self.encryption_key = new_key

            self.fernet = Fernet(self.encryption_key)

    def _encrypt(self, data: str) -> str:
        """Encrypt data string."""
        if not data:
            return data

        try:
            if WINDOWS_AVAILABLE:
                # DPAPI encryption
                # Use current user scope
                encrypted = win32crypt.CryptProtectData(data.encode('utf-8'), None, None, None, None, 0)
                return base64.b64encode(encrypted).decode('ascii')
            else:
                # Fernet encryption
                encrypted = self.fernet.encrypt(data.encode('utf-8'))
                return base64.b64encode(encrypted).decode('ascii')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            # Security: Fail securely. Do not return plaintext.
            raise e

    def _decrypt(self, data: str) -> str:
        """Decrypt data string."""
        if not data:
            return data

        try:
            # Check if it looks like base64
            try:
                decoded = base64.b64decode(data)
            except Exception:
                # Not base64, assume plaintext
                return data

            if WINDOWS_AVAILABLE:
                # DPAPI decryption - returns (description, data)
                decrypted_bytes = win32crypt.CryptUnprotectData(decoded, None, None, None, None, 0)[1]
                return decrypted_bytes.decode('utf-8')
            else:
                # Fernet decryption
                return self.fernet.decrypt(decoded).decode('utf-8')
        except Exception:
            # Failed to decrypt - assume plaintext (legacy data)
            return data

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
                        data TEXT,  -- Encrypted JSON payload
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

            # Security: Ensure database file has strict permissions (0600)
            try:
                self._ensure_secure_permissions(self.db_path)
            except Exception as e:
                logger.warning(f"Could not secure database permissions: {e}")

        except Exception as e:
            logger.error(f"Failed to initialize queue DB: {e}")

    def add(self, endpoint: str, method: str, data: Optional[Dict] = None, 
            priority: int = 1) -> bool:
        """Add a request to the queue."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Serialize
            json_data = json.dumps(data) if data else None

            # Encrypt sensitive data
            try:
                encrypted_data = self._encrypt(json_data)
            except Exception as e:
                logger.error(f"Failed to encrypt request data: {e}")
                return False

            # Note: headers are explicitly NOT stored to prevent leaking tokens/secrets.
            # APIClient relies on current session headers (with fresh token) during retry.
            cursor.execute("""
                INSERT INTO request_queue (endpoint, method, data, headers, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (endpoint, method, encrypted_data, None, priority))
            
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

            items = []
            for row in cursor.fetchall():
                item = dict(row)
                # Decrypt data
                item['data'] = self._decrypt(item['data'])
                items.append(item)

            return items
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
