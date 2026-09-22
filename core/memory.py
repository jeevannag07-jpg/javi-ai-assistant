import sqlite3
import os
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "javi_memory.db")

class JarvisMemory:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes tables for conversation logs and key-value memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for conversation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            # Table for explicit facts / settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_message(self, role: str, content: str):
        """Persists a message in the conversation log."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (role, content) VALUES (?, ?)",
                (role, content)
            )
            conn.commit()

    def get_recent_history(self, limit: int = 6) -> List[Dict[str, str]]:
        """Retrieves the most recent dialogue turns to prime the LLM context."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            # Reverse so it's in chronological order
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def set_fact(self, key: str, value: str):
        """Stores or updates a long-term key/value fact."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_facts (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, value)
            )
            conn.commit()

    def get_all_facts(self) -> Dict[str, str]:
        """Loads all long-term stored facts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_facts")
            return dict(cursor.fetchall())