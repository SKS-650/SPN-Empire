from pydantic import BaseModel
from typing import Optional

class ReminderCreate(BaseModel):
    medicine_name: str
    dosage_metric: str       # e.g., "1 tablet", "5ml"
    frequency_interval: str  # e.g., "Daily", "Twice a day"
    target_time: str         # e.g., "08:00", "20:30"

class ReminderResponse(BaseModel):
    id: int
    medicine_name: str
    dosage_metric: str
    frequency_interval: str
    target_time: str
    is_active: int
    created_at: str

    class Config:
        from_attributes = True