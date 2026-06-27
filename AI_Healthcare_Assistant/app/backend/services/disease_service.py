# Disease Prediction Service
import os
import pickle
import numpy as np
from typing import List

MODEL_DIR = "models/disease_prediction"
MODEL_PATH = os.path.join(MODEL_DIR, "random_forest.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

SYMPTOMS_ORDER = [
    "Fever", "Cough", "Headache", "Fatigue", "Body Ache", 
    "Nausea", "Vomiting", "Diarrhea", "Shortness of Breath", "Loss of Smell"
]

class DiseasePredictionService:
    def __init__(self):
        self.model = None
        self.encoder = None
        self.is_loaded = False
        self.load_model_artifacts()

    def load_model_artifacts(self):
        """Attempts to load the serialized ML model binaries from memory."""
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                with open(ENCODER_PATH, "rb") as f:
                    self.encoder = pickle.load(f)
                self.is_loaded = True
            except Exception:
                self.is_loaded = False

    def predict(self, active_symptoms: List[str]) -> dict:
        """Takes an input list of symptoms, vectorizes them, and returns ML predictions."""
        # Fallback mechanism if the model is missing or hasn't been trained yet
        if not self.is_loaded:
            self.load_model_artifacts() # Retry loading
            if not self.is_loaded:
                return self._get_fallback_prediction(active_symptoms)

        # 1. Vectorize inbound symptoms list into a labelled DataFrame matching model training
        input_vector = {s: (1 if s in active_symptoms else 0) for s in SYMPTOMS_ORDER}
        import pandas as pd
        input_array = pd.DataFrame([input_vector])

        try:
            # 2. Extract classification probabilities
            probabilities = self.model.predict_proba(input_array)[0]
            max_idx = np.argmax(probabilities)
            confidence = probabilities[max_idx]
            
            # 3. Decode the prediction integer into the actual disease name string
            condition = self.encoder.inverse_transform([max_idx])[0]
            
            return {
                "condition": condition,
                "confidence": float(confidence),
                "severity": "High" if "Shortness" in active_symptoms else "Medium" if "Fever" in active_symptoms else "Low",
                "recommendations": self._generate_recommendations(condition)
            }
        except Exception:
            return self._get_fallback_prediction(active_symptoms)

    def _generate_recommendations(self, condition: str) -> List[str]:
        mapping = {
            "Influenza (Flu)": ["Get complete rest", "Drink warm fluids", "Take paracetamol if fever persists"],
            "Gastroenteritis": ["Drink Oral Rehydration Salts (Jeevan Jal)", "Avoid solid foods initially"],
            "Respiratory Infection": ["Monitor breathing oxygen saturation", "Visit nearest health post immediately"],
            "Migraine Profile": ["Rest in a quiet, dark room", "Apply cold compresses to your forehead"]
        }
        return mapping.get(condition, ["Consult with a medical representative at the local community center."])

    def _get_fallback_prediction(self, active_symptoms: List[str]) -> dict:
        """Heuristic rule-based fallback matrix if ML pipelines are offline."""
        if "Fever" in active_symptoms and "Cough" in active_symptoms:
            return {"condition": "Viral Syndrome (Fallback)", "confidence": 0.70, "severity": "Medium", "recommendations": ["Rest", "Hydrate"]}
        return {"condition": "Undetermined Diagnosis", "confidence": 0.50, "severity": "Low", "recommendations": ["Monitor tracking symptoms log."]}

disease_service = DiseasePredictionService()