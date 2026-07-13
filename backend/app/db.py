import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "coding_reviews.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinical_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS code_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL REFERENCES sessions (id),
            code_type TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            explanation TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            reviewed_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def create_session(clinical_text: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO sessions (clinical_text, created_at) VALUES (?, ?)",
        (clinical_text, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def add_code_review(session_id: int, code_type: str, code: dict) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO code_reviews (session_id, code_type, code, description, confidence, explanation, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """,
        (
            session_id,
            code_type,
            code["code"],
            code["description"],
            code["confidence"],
            code.get("explanation"),
        ),
    )
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id


def update_review_status(review_id: int, status: str):
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE code_reviews SET status = ?, reviewed_at = ? WHERE id = ?",
        (status, datetime.now(timezone.utc).isoformat(), review_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    row = None
    if updated:
        row = conn.execute("SELECT * FROM code_reviews WHERE id = ?", (review_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_session(session_id: int):
    conn = get_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    reviews = conn.execute(
        "SELECT * FROM code_reviews WHERE session_id = ?", (session_id,)
    ).fetchall()
    conn.close()

    if session is None:
        return None

    return {
        "session": dict(session),
        "reviews": [dict(r) for r in reviews],
    }
