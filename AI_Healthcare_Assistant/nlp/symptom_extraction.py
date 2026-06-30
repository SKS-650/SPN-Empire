# Symptom Extraction NLP Module
import spacy
from nlp.text_preprocessing import clean_text

class SymptomExtractor:
    def __init__(self):
        # Load a lightweight English NLP entity parser model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model isn't downloaded yet
            self.nlp = None
            
        # Dictionary mapping conversational terms to standard database fields
        self.symptom_dictionary = {
            "fever": "Fever", "hot": "Fever", "temperature": "Fever", "jwaro": "Fever",
            "cough": "Cough", "coughing": "Cough", "khoki": "Cough",
            "head": "Headache", "headache": "Headache", "tauko": "Headache",
            "tired": "Fatigue", "weakness": "Fatigue", "fatigue": "Fatigue",
            "vomit": "Vomiting", "nausea": "Nausea",
            "stomach": "Stomach Ache", "belly": "Stomach Ache", "pait": "Stomach Ache",
            "breath": "Shortness of Breath", "breathing": "Shortness of Breath"
        }

    def extract_symptoms(self, patient_notes: str) -> list:
        """Parses a patient sentence to return an array of confirmed symptom names."""
        if not patient_notes:
            return []
            
        cleaned_notes = clean_text(patient_notes)
        found_symptoms = set()

        # Method 1: Dictionary-based token mapping
        words = cleaned_notes.split()
        for word in words:
            if word in self.symptom_dictionary:
                found_symptoms.add(self.symptom_dictionary[word])

        # Method 2: SpaCy Contextual Parsing fallback
        if self.nlp and len(found_symptoms) == 0:
            doc = self.nlp(patient_notes.lower())
            for token in doc:
                if token.lemma_ in self.symptom_dictionary:
                    found_symptoms.add(self.symptom_dictionary[token.lemma_])

        return list(found_symptoms)

extractor = SymptomExtractor()