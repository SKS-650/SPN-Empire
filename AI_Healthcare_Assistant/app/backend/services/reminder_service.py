# Medicine Reminder Service
import logging
from datetime import datetime
from app.database.database import get_db_connection
from app.backend.schemas.reminder_schema import ReminderCreate

logger = logging.getLogger(__name__)

class ReminderService:
    @staticmethod
    def create_reminder(reminder: ReminderCreate) -> dict:
        """Saves a new medicine reminder schedule into the local SQLite database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO medicine_reminders (medicine_name, dosage_metric, frequency_interval, target_time, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (reminder.medicine_name, reminder.dosage_metric, reminder.frequency_interval, reminder.target_time, created_at))
            
            reminder_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"[🟢] Saved medicine reminder ID {reminder_id} for {reminder.medicine_name}")
            return {"id": reminder_id, "status": "Created successfully"}
        except Exception as e:
            logger.error(f"Failed to create medicine reminder: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_all_reminders() -> list:
        """Fetches all medication reminders from the storage matrix."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicine_reminders ORDER BY target_time ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def delete_reminder(reminder_id: int) -> bool:
        """Deletes a specific medication reminder by its row ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medicine_reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            deleted_rows = cursor.rowcount
            conn.close()
            return deleted_rows > 0
        except Exception as e:
            logger.error(f"Failed to delete reminder {reminder_id}: {e}")
            return False

reminder_service = ReminderService()