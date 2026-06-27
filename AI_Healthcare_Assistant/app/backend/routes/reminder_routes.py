from fastapi import APIRouter, HTTPException, status
from app.backend.schemas.reminder_schema import ReminderCreate, ReminderResponse
from app.backend.services.reminder_service import reminder_service
from typing import List

# Initialize the clean sub-router matrix
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_new_reminder(payload: ReminderCreate):
    """Maps directly to POST http://localhost:8000/api/v1/reminder"""
    result = reminder_service.create_reminder(payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/", response_model=List[ReminderResponse])
def fetch_reminders():
    """Maps directly to GET http://localhost:8000/api/v1/reminder"""
    return reminder_service.get_all_reminders()

@router.delete("/{reminder_id}")
def remove_reminder(reminder_id: int):
    """Maps directly to DELETE http://localhost:8000/api/v1/reminder/{id}"""
    success = reminder_service.delete_reminder(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Medication reminder target ID not found.")
    return {"status": "Deleted successfully", "id": reminder_id}