"""
Database connection and initialisation.
Uses raw sqlite3 for simplicity (no additional dependencies).
"""
import os
import sqlite3

# Resolve paths relative to this file's actual location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "healthcare.db")


def get_db_connection() -> sqlite3.Connection:
    """
    Opens a thread-safe SQLite connection.
    Rows are returned as dict-like sqlite3.Row objects.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database_matrix() -> None:
    """Creates required tables if they don't already exist."""
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Patient history — populated by disease/voice routes after each consultation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_history (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp            TEXT    NOT NULL,
            input_transcript     TEXT,
            translated_symptoms  TEXT,
            ai_predicted_condition TEXT  NOT NULL,
            confidence_score     REAL,
            urgency_level        TEXT    NOT NULL DEFAULT 'ROUTINE',
            medical_advice       TEXT
        )
    """)

    # Medicine reminders — managed by reminder_routes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicine_reminders (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name       TEXT    NOT NULL,
            dosage_metric       TEXT    NOT NULL,
            frequency_interval  TEXT    NOT NULL,
            target_time         TEXT    NOT NULL,
            is_active           INTEGER DEFAULT 1,
            created_at          TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"[🟢] SQLite database ready at {DB_PATH}")


def save_consultation(
    timestamp: str,
    transcript: str,
    symptoms: str,
    condition: str,
    confidence: float,
    urgency: str,
    advice: str,
) -> int:
    """
    Inserts a consultation record into patient_history.
    Returns the new row id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO patient_history
            (timestamp, input_transcript, translated_symptoms,
             ai_predicted_condition, confidence_score, urgency_level, medical_advice)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (timestamp, transcript, symptoms, condition, confidence, urgency, advice),
    )
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_all_consultations() -> list[dict]:
    """Returns all patient history records, newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM patient_history ORDER BY timestamp DESC"
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# Auto-initialise when imported (except when run as __main__)
if __name__ != "__main__":
    initialize_database_matrix()
