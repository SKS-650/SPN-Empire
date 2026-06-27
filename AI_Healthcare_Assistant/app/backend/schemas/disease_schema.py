# Disease Prediction Schemas
from pydantic import BaseModel
from typing import List, Optional

class DiseaseRequest(BaseModel):
    symptoms: List[str]
    notes: Optional[str] = None
    language: str = "en"

class DiseaseResponse(BaseModel):
    condition: str
    confidence: float
    severity: str
    recommendations: List[str]