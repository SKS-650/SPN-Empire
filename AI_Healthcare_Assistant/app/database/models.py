"""
SQLAlchemy ORM models — mirrors the DDL in database.py.
These are optional helpers for code that wants typed ORM access;
the raw sqlite3 layer in database.py is still used by the services.
"""
from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class PatientHistory(Base):
    """
    Stores every AI consultation result so the Health History page
    can display real data instead of dummy records.
    """
    __tablename__ = "patient_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(30), nullable=False)
    input_transcript = Column(Text, nullable=True)
    translated_symptoms = Column(Text, nullable=True)
    ai_predicted_condition = Column(String(200), nullable=False)
    confidence_score = Column(Float, nullable=True)
    urgency_level = Column(String(20), nullable=False, default="ROUTINE")
    medical_advice = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "input_transcript": self.input_transcript,
            "translated_symptoms": self.translated_symptoms,
            "ai_predicted_condition": self.ai_predicted_condition,
            "confidence_score": self.confidence_score,
            "urgency_level": self.urgency_level,
            "medical_advice": self.medical_advice,
        }


class MedicineReminder(Base):
    """Medication schedule entry."""
    __tablename__ = "medicine_reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_name = Column(String(200), nullable=False)
    dosage_metric = Column(String(100), nullable=False)
    frequency_interval = Column(String(100), nullable=False)
    target_time = Column(String(10), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(String(30), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "medicine_name": self.medicine_name,
            "dosage_metric": self.dosage_metric,
            "frequency_interval": self.frequency_interval,
            "target_time": self.target_time,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
