import sqlite3
import os
from datetime import datetime

DB_PATH = "chat_logs.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            role        TEXT NOT NULL,   -- 'user' or 'bot'
            message     TEXT NOT NULL,
            intent      TEXT,
            confidence  TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id   TEXT PRIMARY KEY,
            started_at   TEXT NOT NULL,
            message_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def log_message(session_id: str, role: str, message: str,
                intent: str = None, confidence: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Upsert session
    cur.execute("""
        INSERT INTO sessions (session_id, started_at, message_count)
        VALUES (?, ?, 1)
        ON CONFLICT(session_id) DO UPDATE SET
            message_count = message_count + 1
    """, (session_id, now))

    # Insert message
    cur.execute("""
        INSERT INTO conversations
            (session_id, timestamp, role, message, intent, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, now, role, message, intent, confidence))

    conn.commit()
    conn.close()


def fetch_all_logs() -> list[dict]:
    """Return all conversation logs as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM conversations ORDER BY id DESC LIMIT 500
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_session_stats() -> list[dict]:
    """Return per-session stats."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT session_id, started_at, message_count
        FROM sessions ORDER BY started_at DESC LIMIT 100
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_intent_stats() -> list[dict]:
    """Return intent frequency counts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT intent, COUNT(*) as count
        FROM conversations
        WHERE role = 'user' AND intent IS NOT NULL
        GROUP BY intent ORDER BY count DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def fetch_total_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM conversations")
    total_msgs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
    total_sessions = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM conversations WHERE role = 'user'")
    user_msgs = cur.fetchone()[0]
    conn.close()
    return {
        "total_messages": total_msgs,
        "total_sessions": total_sessions,
        "user_messages": user_msgs,
        "bot_messages": total_msgs - user_msgs,
    }


def clear_all_logs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM conversations")
    cur.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()
