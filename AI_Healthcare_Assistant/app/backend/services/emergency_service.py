"""
Emergency Detection Engine.
Combines a keyword rule engine with an optional ML pkl model.
Works fully offline — the ML model is optional.
"""
import json
import logging
import os
import pickle

import numpy as np

logger = logging.getLogger(__name__)


class EmergencyDetectionEngine:
    def __init__(
        self,
        rules_path: str = "models/emergency_detection/rules.json",
        model_path: str = "models/emergency_detection/emergency_model.pkl",
    ):
        self.rules_path = rules_path
        self.model_path = model_path
        self.rules = self._load_rules()
        self.model = self._load_model()

    # ── Loaders ──────────────────────────────────────────────────────────────
    def _load_rules(self) -> dict:
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Could not load rules.json: {e}")

        # Embedded fallback so the service always starts
        return {
            "critical_keywords": [
                "chest pain", "heart attack", "difficulty breathing",
                "severe bleeding", "unconscious", "stroke", "paralysis",
                "poison", "choking", "can't breathe", "cardiac arrest",
            ],
            "urgent_keywords": [
                "high fever", "snake bite", "severe pain", "bleeding",
                "cannot walk", "loss of balance", "fainted",
            ],
            "severity_levels": {
                "CRITICAL": {
                    "level": 3,
                    "action": (
                        "🚨 CRITICAL: Call emergency services immediately (102 / 112). "
                        "Keep patient calm and still. Do NOT give food or water."
                    ),
                    "color": "red",
                },
                "URGENT": {
                    "level": 2,
                    "action": (
                        "⚠️ URGENT: Visit the nearest health post or hospital within the hour. "
                        "Monitor vital signs continuously."
                    ),
                    "color": "orange",
                },
                "ROUTINE": {
                    "level": 1,
                    "action": (
                        "✅ ROUTINE: Symptoms are not immediately life-threatening. "
                        "Schedule a consultation with your local health worker."
                    ),
                    "color": "green",
                },
            },
        }

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    model = pickle.load(f)
                logger.info("Emergency ML model loaded successfully.")
                return model
            except Exception as e:
                logger.warning(f"Emergency ML model load failed: {e}")
        return None

    # ── Rule engine ───────────────────────────────────────────────────────────
    def _evaluate_text(self, text: str) -> tuple[str, str] | None:
        """
        Scans text for critical/urgent keywords.
        Returns (severity_key, action_message) or None if no match.
        """
        cleaned = text.lower()

        for kw in self.rules.get("critical_keywords", []):
            if kw in cleaned:
                level_data = self.rules["severity_levels"]["CRITICAL"]
                return "CRITICAL", level_data["action"]

        for kw in self.rules.get("urgent_keywords", []):
            if kw in cleaned:
                level_data = self.rules["severity_levels"]["URGENT"]
                return "URGENT", level_data["action"]

        return None

    # ── ML model ──────────────────────────────────────────────────────────────
    def _predict_vector(self, features: dict) -> tuple[str, str]:
        """
        Vector layout expected by the pkl model:
        [chest_pain, breathlessness, high_fever, loss_of_balance, mild_symptoms]
        """
        if not self.model:
            return "UNKNOWN", "ML model not available. Using rule engine only."

        vector = [
            features.get("chest_pain", 0),
            features.get("breathlessness", 0),
            features.get("high_fever", 0),
            features.get("loss_of_balance", 0),
            features.get("mild_symptoms", 0),
        ]

        try:
            prediction = int(self.model.predict([vector])[0])
        except Exception as e:
            logger.error(f"Emergency model prediction failed: {e}")
            return "ROUTINE", self.rules["severity_levels"]["ROUTINE"]["action"]

        levels = self.rules.get("severity_levels", {})
        for key, data in levels.items():
            if data.get("level") == prediction:
                return key, data["action"]

        return "ROUTINE", levels["ROUTINE"]["action"]

    # ── Public API ────────────────────────────────────────────────────────────
    def process_case(
        self,
        user_text: str | None = None,
        symptoms_vector: dict | None = None,
    ) -> dict:
        """
        Routes to rule engine first (text), then ML model (vector).
        Falls back to ROUTINE if neither produces a result.
        """
        # 1. Text-based rule check
        if user_text and user_text.strip():
            rule_result = self._evaluate_text(user_text)
            if rule_result:
                status, action = rule_result
                return {
                    "status": status,
                    "output_message": action,
                    "source": "Rule Engine",
                }

        # 2. ML vector prediction
        if symptoms_vector and any(symptoms_vector.values()):
            status, action = self._predict_vector(symptoms_vector)
            return {
                "status": status,
                "output_message": action,
                "source": "Predictive ML Engine",
            }

        # 3. Default
        routine = self.rules["severity_levels"]["ROUTINE"]
        return {
            "status": "ROUTINE",
            "output_message": routine["action"],
            "source": "Default Engine",
        }
