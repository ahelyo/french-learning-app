# French Learning App (Local, AI-Powered)

A fully local French learning app for A1–B2 learners. Interface and explanations are in English;
the target language is French. Runs entirely on your machine via Ollama — no cloud API calls.

## Features

- **Reading**: generates short stories per CEFR level and theme, with English translation,
  vocabulary list, and grammar notes.
- **Writing**: submit French text, get grammar/spelling corrections with English explanations.
- **Voice Chat**: speak in French (recorded in-browser), get a transcribed + spoken French reply.
- **Static grammar reference** (`data/grammar_a1.json`) is injected into every LLM prompt to reduce
  hallucinated grammar rules. Add `grammar_a2.json`, `grammar_b1.json`, `grammar_b2.json` the same way
  to extend coverage.

## Tech Stack

- **LLM**: [Ollama](https://ollama.com) running locally (default model: `qwen2.5:7b`)
- **Backend**: FastAPI
- **STT**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2-based, fast on CPU)
- **TTS**: [edge-tts](https://github.com/rany2/edge-tts) (free, natural French voices, no local model download)
- **Frontend**: Streamlit

> Edge-TTS requires an internet connection to reach Microsoft's TTS endpoint (it uses no account/API key
> and sends no personal data — just the text to synthesize). If you need a fully offline TTS pipeline,
> swap `backend/audio_service.py` for [Piper TTS](https://github.com/rhasspy/piper) or
> [Coqui TTS](https://github.com/coqui-ai/TTS) — the function signature (`synthesize_speech(text) -> filename`)
> is designed to be swappable.

## Setup

### 1. Install Ollama and pull a model

```bash
ollama pull qwen2.5:7b
```

(Or `llama3:8b` — update `OLLAMA_MODEL` in `.env` to match.)

### 2. Create a Python virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env
```

Edit `.env` if you want a different model, Whisper size, or TTS voice.

### 4. Run the backend

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Run the frontend (in a second terminal, venv activated)

```bash
streamlit run frontend/app.py
```

The app opens at `http://localhost:8501`. Make sure Ollama is running (`ollama serve`, usually automatic)
before generating stories or chatting.

## Project Structure

```
backend/
  main.py          FastAPI app and endpoints
  llm_service.py    Ollama integration & master prompts (CEFR-aware)
  audio_service.py  Whisper STT & Edge-TTS
  config.py         Settings loaded from .env
  schemas.py        Pydantic request/response models
data/
  grammar_a1.json   Static grammar rules (extend per level)
  stories_cache/    Generated stories, cached by (level, theme) hash
  audio_cache/      Generated TTS audio files
frontend/
  app.py            Streamlit UI: Reading / Writing / Voice Chat tabs
```

## Notes

- First request to `/api/chat/voice` or `/api/story/generate` may be slow while Ollama loads the model
  into memory and faster-whisper downloads/loads its model weights.
- `st.audio_input` (used for voice recording) requires Streamlit ≥ 1.38, pinned in `requirements.txt`.
- Story cache keys are a hash of `(level, theme)` — delete files in `data/stories_cache/` to force
  regeneration of a specific story.
