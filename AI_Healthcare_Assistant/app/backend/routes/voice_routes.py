"""
Voice Assistant API routes.
Provides two endpoints:
  POST /process          — full STT → NLP → TTS pipeline (gTTS / Google STT)
  POST /transcribe/whisper — Whisper-only transcription
"""
import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.backend.services.voice_service import VoiceConsultationService, VoiceService

router = APIRouter()

# Singletons
_consultation_svc = VoiceConsultationService()
_whisper_svc = VoiceService()


# ── Full pipeline: STT → NLP → gTTS ─────────────────────────────────────────
@router.post("/process")
async def process_voice_pipeline(file: UploadFile = File(...)):
    """
    Accepts a WAV/MP3 audio file, transcribes it (Google STT with Nepali fallback),
    runs the NLP consultation engine, generates a Nepali TTS reply, and returns
    the full result including a URL to the synthesised audio file.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No audio file stream detected.")

    try:
        raw_audio_bytes = await file.read()
        result = _consultation_svc.process_voice_buffer(
            audio_bytes=raw_audio_bytes,
            filename=file.filename or "upload.wav",
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Whisper transcription only ───────────────────────────────────────────────
@router.post("/transcribe/whisper")
async def transcribe_whisper(file: UploadFile = File(...)):
    """
    Accepts an audio file and returns a plain-text transcription using
    OpenAI Whisper (runs fully offline after the first model download).
    """
    temp_dir = os.path.join("temp_audio")
    os.makedirs(temp_dir, exist_ok=True)

    safe_name = os.path.basename(file.filename or "audio.wav")
    temp_path = os.path.join(temp_dir, safe_name)

    try:
        with open(temp_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        result = await _whisper_svc.process_voice_with_whisper(temp_path)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
