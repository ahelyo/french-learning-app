from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORIES_CACHE_DIR = DATA_DIR / "stories_cache"
AUDIO_CACHE_DIR = DATA_DIR / "audio_cache"
GRAMMAR_DIR = DATA_DIR


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma4:31b-cloud"
    ollama_api_key: str = ""

    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    tts_voice: str = "fr-FR-DeniseNeural"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()

# On Streamlit Cloud (or anywhere with no local `ollama serve` daemon), the app talks to
# Ollama's cloud API directly with an API key instead of via localhost:11434.
try:
    import streamlit as st

    if st.secrets.get("OLLAMA_API_KEY"):
        settings.ollama_api_key = st.secrets["OLLAMA_API_KEY"]
    if st.secrets.get("OLLAMA_HOST"):
        settings.ollama_host = st.secrets["OLLAMA_HOST"]
    if st.secrets.get("OLLAMA_MODEL"):
        settings.ollama_model = st.secrets["OLLAMA_MODEL"]
except Exception:
    pass

STORIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
