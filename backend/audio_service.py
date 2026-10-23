import uuid

import edge_tts
from faster_whisper import WhisperModel

from backend.config import AUDIO_CACHE_DIR, settings

_whisper_model: WhisperModel | None = None


def _get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
    return _whisper_model


def transcribe_audio(file_path: str, language: str = "fr") -> str:
    model = _get_whisper_model()
    segments, _ = model.transcribe(file_path, language=language)
    return " ".join(segment.text.strip() for segment in segments).strip()


async def synthesize_speech(text: str, filename: str | None = None) -> str:
    filename = filename or f"{uuid.uuid4().hex}.mp3"
    out_path = AUDIO_CACHE_DIR / filename
    if not out_path.exists():
        communicate = edge_tts.Communicate(text, settings.tts_voice)
        await communicate.save(str(out_path))
    return filename
