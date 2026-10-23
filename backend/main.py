import hashlib
import json
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend import audio_service, llm_service
from backend.config import AUDIO_CACHE_DIR, GRAMMAR_DIR, STORIES_CACHE_DIR
from backend.schemas import (
    CEFRLevel,
    ChatMessage,
    ChatTextRequest,
    ChatTextResponse,
    ChatVoiceResponse,
    LibraryStoryItem,
    StoryCreateRequest,
    StoryRequest,
    StoryResponse,
    WritingCorrectionRequest,
    WritingCorrectionResponse,
)

_LEVEL_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
_LENGTH_ORDER = {"short": 0, "medium": 1, "long": 2}


def _infer_length(story_fr: str) -> str:
    words = len(story_fr.split())
    if words >= 500:
        return "long"
    if words >= 150:
        return "medium"
    return "short"

app = FastAPI(title="French Learning App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/grammar/{level}")
def get_grammar(level: CEFRLevel):
    path = GRAMMAR_DIR / f"grammar_{level.lower()}.json"
    if not path.exists():
        raise HTTPException(404, f"No grammar data for level {level}")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/story/generate", response_model=StoryResponse)
async def generate_story(req: StoryRequest):
    cache_key = hashlib.sha256(f"{req.level}:{req.theme}:{req.length}".encode()).hexdigest()[:16]
    cache_path = STORIES_CACHE_DIR / f"{cache_key}.json"
    if cache_path.exists():
        result = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        try:
            result = llm_service.generate_story(req.level, req.theme, req.length)
        except (json.JSONDecodeError, KeyError) as exc:
            raise HTTPException(502, f"Model returned an invalid story: {exc}") from exc

        result["level"] = req.level
        result["theme"] = req.theme
        result["length"] = req.length
        cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    result.setdefault("length", req.length)
    audio_filename = await audio_service.synthesize_speech(result["story_fr"], filename=f"{cache_key}.mp3")
    result["audio_url"] = f"/api/audio/{audio_filename}"
    return result


@app.get("/api/story/library", response_model=list[LibraryStoryItem])
def list_story_library():
    items = []
    for path in STORIES_CACHE_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        items.append(
            LibraryStoryItem(
                cache_key=path.stem,
                level=data["level"],
                length=data.get("length") or _infer_length(data.get("story_fr", "")),
                theme=data["theme"],
                title_fr=data["title_fr"],
                title_en=data["title_en"],
            )
        )
    items.sort(key=lambda i: (_LEVEL_ORDER[i.level], _LENGTH_ORDER[i.length], i.theme.lower()))
    return items


@app.get("/api/story/library/{cache_key}", response_model=StoryResponse)
async def get_library_story(cache_key: str):
    safe_key = Path(cache_key).name
    cache_path = STORIES_CACHE_DIR / f"{safe_key}.json"
    if not cache_path.exists():
        raise HTTPException(404, "Story not found")

    result = json.loads(cache_path.read_text(encoding="utf-8"))
    if "length" not in result:
        result["length"] = _infer_length(result.get("story_fr", ""))
    audio_filename = await audio_service.synthesize_speech(result["story_fr"], filename=f"{safe_key}.mp3")
    result["audio_url"] = f"/api/audio/{audio_filename}"
    return result


@app.post("/api/story/library", response_model=StoryResponse)
async def add_story_to_library(req: StoryCreateRequest):
    cache_key = uuid.uuid4().hex[:16]
    cache_path = STORIES_CACHE_DIR / f"{cache_key}.json"
    result = {
        "title_fr": req.title_fr,
        "title_en": req.title_en,
        "story_fr": req.story_fr,
        "story_en": req.story_en,
        "vocabulary": [item.model_dump() for item in req.vocabulary],
        "grammar_notes": req.grammar_notes,
        "level": req.level,
        "theme": req.theme,
        "length": req.length,
    }
    cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    audio_filename = await audio_service.synthesize_speech(result["story_fr"], filename=f"{cache_key}.mp3")
    result["audio_url"] = f"/api/audio/{audio_filename}"
    return result


@app.post("/api/writing/correct", response_model=WritingCorrectionResponse)
def correct_writing(req: WritingCorrectionRequest):
    try:
        return llm_service.correct_writing(req.text, req.level)
    except (json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(502, f"Model returned an invalid correction: {exc}") from exc


@app.post("/api/chat/text", response_model=ChatTextResponse)
def chat_text(req: ChatTextRequest):
    try:
        return llm_service.chat_reply(req.level, req.history, req.message)
    except (json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(502, f"Model returned an invalid reply: {exc}") from exc


@app.post("/api/chat/voice", response_model=ChatVoiceResponse)
async def chat_voice(
    level: CEFRLevel = Form(...),
    history: str = Form("[]"),
    audio: UploadFile = File(...),
):
    history_items = [ChatMessage(**m) for m in json.loads(history)]

    with tempfile.NamedTemporaryFile(suffix=Path(audio.filename or "audio.wav").suffix, delete=False) as tmp:
        shutil.copyfileobj(audio.file, tmp)
        tmp_path = tmp.name

    try:
        transcript = audio_service.transcribe_audio(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not transcript:
        raise HTTPException(400, "Could not transcribe any speech from the audio.")

    try:
        reply = llm_service.chat_reply(level, history_items, transcript)
    except (json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(502, f"Model returned an invalid reply: {exc}") from exc

    audio_filename = await audio_service.synthesize_speech(reply["reply_fr"])

    return ChatVoiceResponse(
        transcript_fr=transcript,
        reply_fr=reply["reply_fr"],
        reply_en=reply["reply_en"],
        audio_url=f"/api/audio/{audio_filename}",
    )


@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    path = AUDIO_CACHE_DIR / Path(filename).name
    if not path.exists():
        raise HTTPException(404, "Audio file not found")
    return FileResponse(path, media_type="audio/mpeg")
