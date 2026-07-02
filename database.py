import sqlite3
from pathlib import Path

DB_PATH = Path("checkpoints/checkpoints.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, payload TEXT)")
    conn.commit()
    conn.close()
