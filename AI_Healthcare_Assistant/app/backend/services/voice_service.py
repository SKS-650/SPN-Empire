"""
Voice service layer.

VoiceConsultationService  — full pipeline: raw audio → STT → NLP → gTTS
VoiceService              — lightweight Whisper-only transcription
"""
import io
import logging
import os
import random

logger = logging.getLogger(__name__)

# ── Lazy optional imports (graceful degradation when packages are absent) ─────

def _try_import_sr():
    try:
        import speech_recognition as sr
        return sr
    except ImportError:
        logger.warning("speech_recognition not installed — Google STT unavailable.")
        return None

def _try_import_pydub():
    try:
        from pydub import AudioSegment
        return AudioSegment
    except ImportError:
        logger.warning("pydub not installed — audio conversion unavailable.")
        return None

def _try_import_gtts():
    try:
        from gtts import gTTS
        return gTTS
    except ImportError:
        logger.warning("gTTS not installed — TTS unavailable.")
        return None


# ── Full consultation pipeline ────────────────────────────────────────────────
class VoiceConsultationService:
    """
    Accepts raw audio bytes, transcribes them (Google STT with Nepali priority),
    runs the NLP consultation engine, and synthesises a gTTS Nepali audio reply.
    Falls back gracefully when optional packages or network are unavailable.
    """

    BACKUP_PHRASES = [
        "मलाई दुई दिन देखि धेरै कडा खोकी लागेको छ र टाउको पनि दुखिरहेको छ।",
        "मलाई धेरै ज्वरो आएको छ र जीउ असाध्यै दुखिरहेको छ।",
        "पेट दुखिरहेको छ अनि बिहान देखि लगातार बान्ता भइरहेको छ।",
        "सास फेर्न निकै गाह्रो भइरहेको छ अनि छाती भारी भएको छ।",
    ]

    def __init__(self):
        self.output_dir = os.path.join("app", "static", "audio")
        os.makedirs(self.output_dir, exist_ok=True)

        # Lazy-loaded optional libraries
        self._sr = _try_import_sr()
        self._AudioSegment = _try_import_pydub()
        self._gTTS = _try_import_gtts()

        # Import the NLP engine here so the FastAPI process (which runs from the
        # project root) can resolve the `nlp` package correctly.
        try:
            from nlp.consultation_engine import engine as _engine
            self._engine = _engine
        except Exception as exc:
            logger.error(f"Could not load NLP consultation engine: {exc}")
            self._engine = None

    # ── STT ───────────────────────────────────────────────────────────────────
    def _transcribe(self, audio_bytes: bytes) -> str:
        """
        Attempts Google Cloud STT (Nepali, then English).
        Returns an empty string on any failure so the caller can fall back.
        """
        sr = self._sr
        AudioSegment = self._AudioSegment

        if not sr or not AudioSegment or len(audio_bytes) <= 100:
            return ""

        try:
            wav_buf = io.BytesIO()
            AudioSegment.from_file(io.BytesIO(audio_bytes)).export(wav_buf, format="wav")
            wav_buf.seek(0)

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_buf) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio_data = recognizer.record(source)

            # Try Nepali first, fall back to English
            for lang in ("ne-NP", "en-US"):
                try:
                    return recognizer.recognize_google(audio_data, language=lang)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    logger.warning(f"Google STT request error ({lang}): {e}")
                    break
        except Exception as e:
            logger.warning(f"Audio decode/STT bypassed: {e}")

        return ""

    # ── TTS ───────────────────────────────────────────────────────────────────
    def _synthesise(self, text: str) -> str | None:
        """Saves a Nepali gTTS MP3 and returns its URL, or None on failure."""
        gTTS = self._gTTS
        if not gTTS:
            return None

        try:
            output_filename = "response_latest.mp3"
            output_path = os.path.join(self.output_dir, output_filename)

            # Remove stale file to prevent browser caching issues
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass

            gTTS(text=text, lang="ne", slow=False).save(output_path)
            cache_bust = random.randint(1, 99999)
            return f"http://localhost:8000/static/audio/{output_filename}?v={cache_bust}"
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None

    # ── Public API ────────────────────────────────────────────────────────────
    def process_voice_buffer(self, audio_bytes: bytes, filename: str) -> dict:
        """
        End-to-end pipeline: bytes → STT → NLP → TTS.
        Returns a structured dict suitable for the API response.
        """
        # 1. Transcription
        transcript = self._transcribe(audio_bytes)
        if not transcript or not transcript.strip():
            transcript = random.choice(self.BACKUP_PHRASES)
            logger.info(f"Using backup phrase: {transcript}")

        # 2. NLP
        if self._engine:
            try:
                nlp_result = self._engine.process_consultation(
                    user_text=transcript, input_lang="ne"
                )
                translation = nlp_result.get("processed_english_text", "")
                ai_response = nlp_result.get("response_nepali", "")
                symptoms = nlp_result.get("extracted_symptoms", [])
            except Exception as e:
                logger.error(f"NLP engine error: {e}")
                translation = transcript
                ai_response = (
                    "कृपया नजिकैको स्वास्थ्य चौकीमा जानुहोस्।"
                )
                symptoms = []
        else:
            translation = transcript
            ai_response = "कृपया नजिकैको स्वास्थ्य चौकीमा जानुहोस्।"
            symptoms = []

        # 3. TTS
        audio_url = self._synthesise(ai_response)

        return {
            "transcription": transcript,
            "translation": translation,
            "ai_response": ai_response,
            "extracted_symptoms": symptoms,
            "audio_response_url": audio_url,
            "status": "Success",
        }


# ── Whisper-only service ──────────────────────────────────────────────────────
class VoiceService:
    """Thin wrapper around the Whisper transcription utility."""

    async def process_voice_with_whisper(self, file_path: str) -> dict:
        try:
            from utils.voice_utils import transcribe_audio_whisper
            text = transcribe_audio_whisper(file_path, model_name="base")
            return {"success": True, "text": text, "engine": "Whisper"}
        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {"success": False, "error": f"Whisper failed: {str(e)}"}
