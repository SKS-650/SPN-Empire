"""
Disease prediction API route.
POST /predict  — runs the Random Forest model and saves the result to history.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.backend.schemas.disease_schema import DiseaseRequest, DiseaseResponse
from app.backend.services.disease_service import disease_service
from app.database.database import save_consultation

router = APIRouter()

# Lazy-load translator so the route still works if deep_translator is absent
def _get_translator():
    try:
        from nlp.nepali_translation import translator
        return translator
    except Exception:
        return None


@router.post("/predict", response_model=DiseaseResponse)
async def predict_disease(payload: DiseaseRequest):
    try:
        result = disease_service.predict(payload.symptoms)

        condition = result["condition"]
        recommendations = result["recommendations"]

        # Optional Nepali translation
        if payload.language == "np":
            translator = _get_translator()
            if translator:
                try:
                    condition = translator.translate_to_nepali(condition)
                    recommendations = [
                        translator.translate_to_nepali(r) for r in recommendations
                    ]
                except Exception:
                    pass  # Fall back to English if translation fails

        # Persist consultation in the local health history
        try:
            save_consultation(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                transcript=payload.notes or "",
                symptoms=", ".join(payload.symptoms),
                condition=result["condition"],   # always save English internally
                confidence=result["confidence"],
                urgency=result["severity"].upper(),
                advice="; ".join(result["recommendations"]),
            )
        except Exception:
            pass  # History saving failure must never break the prediction response

        return DiseaseResponse(
            condition=condition,
            confidence=result["confidence"],
            severity=result["severity"],
            recommendations=recommendations,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
