"""
Emergency Alert API routes.
Wires the real EmergencyDetectionEngine into the /trigger endpoint and adds
a new /assess endpoint for symptom-vector triage.
"""
import sys
import os

# Ensure the project root is on the path when this module is imported directly
_project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.backend.services.emergency_service import EmergencyDetectionEngine

router = APIRouter()

# Singleton engine (loads rules.json + pkl model at startup)
_engine = EmergencyDetectionEngine(
    rules_path=os.path.join(_project_root, "models", "emergency_detection", "rules.json"),
    model_path=os.path.join(_project_root, "models", "emergency_detection", "emergency_model.pkl"),
)


# ── Request/Response schemas ─────────────────────────────────────────────────
class EmergencyPayload(BaseModel):
    location: str
    type: str
    description: str


class AssessPayload(BaseModel):
    description: Optional[str] = None
    chest_pain: int = 0
    breathlessness: int = 0
    high_fever: int = 0
    loss_of_balance: int = 0
    mild_symptoms: int = 0


# ── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/trigger")
async def trigger_sos(payload: EmergencyPayload):
    """
    Broadcast an emergency SOS.
    Also evaluates the description text through the rule engine to assign
    a triage severity level before dispatching.
    """
    if not payload.location or not payload.location.strip():
        raise HTTPException(status_code=400, detail="Geographic location is required.")

    # Run the description through the emergency engine
    combined_text = f"{payload.type}. {payload.description}"
    triage = _engine.process_case(user_text=combined_text)

    severity = triage.get("status", "ROUTINE")
    action_msg = triage.get("output_message", "")

    color_map = {"CRITICAL": "🔴", "URGENT": "🟡", "ROUTINE": "🟢"}
    indicator = color_map.get(severity, "🟢")

    return {
        "status": "Broadcasting",
        "severity": severity,
        "indicator": indicator,
        "action_message": action_msg,
        "broadcast_id": f"SOS-{abs(hash(payload.location)) % 9999:04d}-NP",
        "target_nodes": [
            "Nearest District Health Post",
            "NCIT Rural Emergency Relay",
            "Sindhupalchok District Hospital",
        ],
        "source": triage.get("source", "Rule Engine"),
    }


@router.post("/assess")
async def assess_severity(payload: AssessPayload):
    """
    Assess triage severity from free-text description or symptom binary vector.
    Useful for the frontend to determine urgency before triggering a full SOS.
    """
    symptoms_vector = {
        "chest_pain":      payload.chest_pain,
        "breathlessness":  payload.breathlessness,
        "high_fever":      payload.high_fever,
        "loss_of_balance": payload.loss_of_balance,
        "mild_symptoms":   payload.mild_symptoms,
    }

    result = _engine.process_case(
        user_text=payload.description,
        symptoms_vector=symptoms_vector if any(symptoms_vector.values()) else None,
    )

    color_map = {"CRITICAL": "🔴", "URGENT": "🟡", "ROUTINE": "🟢"}
    result["indicator"] = color_map.get(result.get("status", "ROUTINE"), "🟢")
    return result
