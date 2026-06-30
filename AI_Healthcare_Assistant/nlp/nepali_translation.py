# Nepali Language Translation Module
import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class NepaliTranslator:
    def __init__(self):
        # Initialize translators for bidirectional conversion
        self.to_english_engine = GoogleTranslator(source='ne', target='en')
        self.to_nepali_engine = GoogleTranslator(source='en', target='ne')

    def translate_to_english(self, nepali_text: str) -> str:
        """Converts local Nepali input text to English for AI models."""
        if not nepali_text or not nepali_text.strip():
            return ""
        try:
            return self.to_english_engine.translate(nepali_text)
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return nepali_text  # Fallback to original text if offline or error occurs

    def translate_to_nepali(self, english_text: str) -> str:
        """Converts English diagnostic text to local Nepali language."""
        if not english_text or not english_text.strip():
            return ""
        try:
            return self.to_nepali_engine.translate(english_text)
        except Exception as e:
            logger.error(f"Translation to Nepali failed: {e}")
            return english_text

# Singleton instance for global app usage
translator = NepaliTranslator()