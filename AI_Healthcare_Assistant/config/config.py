"""
Central application configuration.
Values can be overridden via environment variables or secrets.env.
"""
import os
from dotenv import load_dotenv

# Load secrets.env from the same directory
_env_path = os.path.join(os.path.dirname(__file__), "secrets.env")
load_dotenv(_env_path)

# ── Server settings ───────────────────────────────────────────────────────────
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "app", "database", "healthcare.db"),
)

# ── Model paths ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

DISEASE_MODEL_PATH  = os.path.join(MODELS_DIR, "disease_prediction", "random_forest.pkl")
DISEASE_ENCODER_PATH = os.path.join(MODELS_DIR, "disease_prediction", "label_encoder.pkl")

SKIN_MODEL_PATH  = os.path.join(MODELS_DIR, "skin_detection", "mobilenet_skin.pt")
SKIN_LABELS_PATH = os.path.join(MODELS_DIR, "skin_detection", "classes.txt")

EMERGENCY_RULES_PATH = os.path.join(MODELS_DIR, "emergency_detection", "rules.json")
EMERGENCY_MODEL_PATH = os.path.join(MODELS_DIR, "emergency_detection", "emergency_model.pkl")

# ── Audio output ──────────────────────────────────────────────────────────────
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "app", "static", "audio")

# ── Feature flags ─────────────────────────────────────────────────────────────
ENABLE_WHISPER      = os.getenv("ENABLE_WHISPER", "true").lower() == "true"
ENABLE_GOOGLE_STT   = os.getenv("ENABLE_GOOGLE_STT", "true").lower() == "true"
ENABLE_GTTS         = os.getenv("ENABLE_GTTS", "true").lower() == "true"
OFFLINE_MODE        = os.getenv("OFFLINE_MODE", "false").lower() == "true"

# ── OpenAI ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
