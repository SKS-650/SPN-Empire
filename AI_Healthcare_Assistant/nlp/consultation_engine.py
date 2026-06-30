# Consultation Engine Module
from nlp.nepali_translation import translator
from nlp.symptom_extraction import extractor

class ConsultationEngine:
    def __init__(self):
        pass

    def process_consultation(self, user_text: str, input_lang: str = "ne") -> dict:
        """
        Runs the end-to-end NLP consultation processing chain.
        Transcribes/translates -> Extracts Symptoms -> Formats Response Packet.
        """
        original_text = user_text
        working_english_text = user_text

        # 1. Handle cross-language translation mappings if necessary
        if input_lang == "ne":
            working_english_text = translator.translate_to_english(user_text)

        # 2. Parse structural health components out of the text string
        extracted_symptoms = extractor.extract_symptoms(working_english_text)

        # 3. Create contextual response strings
        if not extracted_symptoms:
            eng_advice = "Could you please describe your clinical systems or pain areas more clearly?"
        else:
            eng_advice = f"System identified patterns matching: {', '.join(extracted_symptoms)}. Please visit the nearest primary healthcare outpost if conditions persist."

        # 4. Prepare local language feedback
        nepali_advice = translator.translate_to_nepali(eng_advice)

        return {
            "processed_english_text": working_english_text,
            "extracted_symptoms": extracted_symptoms,
            "response_english": eng_advice,
            "response_nepali": nepali_advice
        }

engine = ConsultationEngine()