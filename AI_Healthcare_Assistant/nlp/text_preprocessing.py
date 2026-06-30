# Text Preprocessing Module
import re

def clean_text(text: str) -> str:
    """Removes special characters, extra whitespaces, and normalizes text input."""
    if not text:
        return ""
    # Lowercase text
    text = text.lower()
    # Remove punctuation and special symbols (keeps spaces and alphanumeric)
    text = re.sub(r'[^\w\s\u0900-\u097F]', '', text) 
    # Remove duplicate spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_text(text: str) -> list:
    """Splits text sentences safely into individual words or structural lists."""
    cleaned = clean_text(text)
    return cleaned.split(" ")