import asyncio
import hashlib
import json
import uuid
from pathlib import Path

from backend import audio_service, llm_service
from backend.config import GRAMMAR_DIR, STORIES_CACHE_DIR
from backend.schemas import CEFRLevel, ChatMessage, StoryLength, VocabItem

_LEVEL_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
_LENGTH_ORDER = {"short": 0, "medium": 1, "long": 2}


class AppError(Exception):
    pass


def _infer_length(story_fr: str) -> str:
    words = len(story_fr.split())
    if words >= 500:
        return "long"
    if words >= 150:
        return "medium"
    return "short"


def get_grammar(level: CEFRLevel) -> dict:
    path = GRAMMAR_DIR / f"grammar_{level.lower()}.json"
    if not path.exists():
        raise AppError(f"No grammar data for level {level}")
    return json.loads(path.read_text(encoding="utf-8"))


def get_daily_phrases() -> dict:
    path = GRAMMAR_DIR / "daily_phrases.json"
    if not path.exists():
        raise AppError("No daily phrases data found")
    return json.loads(path.read_text(encoding="utf-8"))


def generate_story(level: CEFRLevel, theme: str, length: StoryLength) -> dict:
    cache_key = hashlib.sha256(f"{level}:{theme}:{length}".encode()).hexdigest()[:16]
    cache_path = STORIES_CACHE_DIR / f"{cache_key}.json"
    if cache_path.exists():
        result = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        try:
            result = llm_service.generate_story(level, theme, length)
        except (json.JSONDecodeError, KeyError) as exc:
            raise AppError(f"Model returned an invalid story: {exc}") from exc

        result["level"] = level
        result["theme"] = theme
        result["length"] = length
        cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    result.setdefault("length", length)
    audio_filename = asyncio.run(audio_service.synthesize_speech(result["story_fr"], filename=f"{cache_key}.mp3"))
    result["audio_path"] = str(audio_service.AUDIO_CACHE_DIR / audio_filename)
    return result


def list_story_library() -> list[dict]:
    items = []
    for path in STORIES_CACHE_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        items.append(
            {
                "cache_key": path.stem,
                "level": data["level"],
                "length": data.get("length") or _infer_length(data.get("story_fr", "")),
                "theme": data["theme"],
                "title_fr": data["title_fr"],
                "title_en": data["title_en"],
            }
        )
    items.sort(key=lambda i: (_LEVEL_ORDER[i["level"]], _LENGTH_ORDER[i["length"]], i["theme"].lower()))
    return items


def get_library_story(cache_key: str) -> dict:
    safe_key = Path(cache_key).name
    cache_path = STORIES_CACHE_DIR / f"{safe_key}.json"
    if not cache_path.exists():
        raise AppError("Story not found")

    result = json.loads(cache_path.read_text(encoding="utf-8"))
    if "length" not in result:
        result["length"] = _infer_length(result.get("story_fr", ""))
    audio_filename = asyncio.run(audio_service.synthesize_speech(result["story_fr"], filename=f"{safe_key}.mp3"))
    result["audio_path"] = str(audio_service.AUDIO_CACHE_DIR / audio_filename)
    return result


def add_story_to_library(
    level: CEFRLevel,
    length: StoryLength,
    theme: str,
    title_fr: str,
    title_en: str,
    story_fr: str,
    story_en: str,
    vocabulary: list[VocabItem] | None = None,
    grammar_notes: list[str] | None = None,
) -> dict:
    cache_key = uuid.uuid4().hex[:16]
    cache_path = STORIES_CACHE_DIR / f"{cache_key}.json"
    result = {
        "title_fr": title_fr,
        "title_en": title_en,
        "story_fr": story_fr,
        "story_en": story_en,
        "vocabulary": [v.model_dump() if isinstance(v, VocabItem) else v for v in (vocabulary or [])],
        "grammar_notes": grammar_notes or [],
        "level": level,
        "theme": theme,
        "length": length,
    }
    cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    audio_filename = asyncio.run(audio_service.synthesize_speech(result["story_fr"], filename=f"{cache_key}.mp3"))
    result["audio_path"] = str(audio_service.AUDIO_CACHE_DIR / audio_filename)
    return result


def correct_writing(text: str, level: CEFRLevel) -> dict:
    try:
        return llm_service.correct_writing(text, level)
    except (json.JSONDecodeError, KeyError) as exc:
        raise AppError(f"Model returned an invalid correction: {exc}") from exc


def chat_text(level: CEFRLevel, history: list[ChatMessage], message: str) -> dict:
    try:
        return llm_service.chat_reply(level, history, message)
    except (json.JSONDecodeError, KeyError) as exc:
        raise AppError(f"Model returned an invalid reply: {exc}") from exc


def chat_voice(level: CEFRLevel, history: list[ChatMessage], audio_bytes: bytes, suffix: str = ".wav") -> dict:
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        transcript = audio_service.transcribe_audio(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not transcript:
        raise AppError("Could not transcribe any speech from the audio.")

    try:
        reply = llm_service.chat_reply(level, history, transcript)
    except (json.JSONDecodeError, KeyError) as exc:
        raise AppError(f"Model returned an invalid reply: {exc}") from exc

    audio_filename = asyncio.run(audio_service.synthesize_speech(reply["reply_fr"]))

    return {
        "transcript_fr": transcript,
        "reply_fr": reply["reply_fr"],
        "reply_en": reply["reply_en"],
        "audio_path": str(audio_service.AUDIO_CACHE_DIR / audio_filename),
    }
