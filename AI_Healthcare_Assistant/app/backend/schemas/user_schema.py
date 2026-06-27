# User Schemas
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    user_id: str
    full_name: str
    age: int
    district: str
    emergency_contact: str