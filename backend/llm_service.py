import json

import ollama

from backend.config import GRAMMAR_DIR, settings
from backend.schemas import CEFRLevel, ChatMessage, StoryLength

if settings.ollama_api_key:
    # No local `ollama serve` daemon available (e.g. Streamlit Cloud) -- talk to Ollama's
    # cloud API directly. Direct API calls use the bare model name, without the "-cloud"
    # suffix the local daemon's own proxy naming uses.
    _client = ollama.Client(host="https://ollama.com", headers={"Authorization": f"Bearer {settings.ollama_api_key}"})
    _MODEL = settings.ollama_model.removesuffix("-cloud")
else:
    _client = ollama.Client(host=settings.ollama_host)
    _MODEL = settings.ollama_model

_LEVEL_DESCRIPTIONS = {
    "A1": "beginner: present tense only, simple short sentences, ~300 common words",
    "A2": "elementary: present + passé composé, everyday topics, ~600 words",
    "B1": "intermediate: most tenses including subjunctive for basic opinions, longer sentences",
    "B2": "upper-intermediate: nuanced tenses and connectors, idiomatic expressions",
}

_LENGTH_SPECS = {
    "short": {"sentences": "4-6 sentences, about 60-100 words total", "vocab": "8-10", "grammar_notes": "2-3"},
    "medium": {
        "sentences": "10-15 sentences across 2-3 short paragraphs, about 250-350 words total",
        "vocab": "12-16",
        "grammar_notes": "3-4",
    },
    "long": {
        "sentences": (
            "at least 800 words total (roughly 4 pages), across 10-14 paragraphs of 4-8 sentences each -- "
            "do not stop early, the word count is a hard minimum"
        ),
        "vocab": "20-30",
        "grammar_notes": "6-8",
    },
}

_BASE_SYSTEM_PROMPT = (
    "You are a French language tutor for English-speaking learners. "
    "You always respond with valid JSON only, matching the schema you are given, "
    "with no markdown fences and no commentary outside the JSON object. "
    "Ground every grammar claim in standard French grammar; never invent conjugations or rules."
)


def _load_grammar_reference(level: CEFRLevel) -> str:
    path = GRAMMAR_DIR / f"grammar_{level.lower()}.json"
    if not path.exists():
        path = GRAMMAR_DIR / "grammar_a1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    topics = [f"- {t['title']}: {t.get('explanation_en', '')}" for t in data.get("topics", [])]
    return "Reference grammar points available for this level:\n" + "\n".join(topics)


def _chat_json(system: str, user: str) -> dict:
    response = _client.chat(
        model=_MODEL,
        format="json",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = response["message"]["content"]
    return json.loads(content)


def generate_story(level: CEFRLevel, theme: str, length: StoryLength = "short") -> dict:
    grammar_ref = _load_grammar_reference(level)
    spec = _LENGTH_SPECS[length]
    system = (
        f"{_BASE_SYSTEM_PROMPT}\n"
        f"Target CEFR level: {level} ({_LEVEL_DESCRIPTIONS[level]}).\n"
        f"{grammar_ref}\n"
        "Respond with JSON matching exactly this schema:\n"
        "{\n"
        '  "title_fr": string, "title_en": string,\n'
        f'  "story_fr": string ({spec["sentences"]}, appropriate to the level),\n'
        '  "story_en": string (full English translation),\n'
        f'  "vocabulary": [{{"french": string, "english": string}}] ({spec["vocab"]} key words/phrases from the story),\n'
        f'  "grammar_notes": [string] ({spec["grammar_notes"]} short English notes on grammar points used in the story)\n'
        "}"
    )
    user = f"Write a story in French about the theme: \"{theme}\"."
    return _chat_json(system, user)


def correct_writing(text: str, level: CEFRLevel) -> dict:
    grammar_ref = _load_grammar_reference(level)
    system = (
        f"{_BASE_SYSTEM_PROMPT}\n"
        f"The student is at CEFR level {level}.\n"
        f"{grammar_ref}\n"
        "Respond with JSON matching exactly this schema:\n"
        "{\n"
        '  "corrected_text": string (the full corrected French text),\n'
        '  "corrections": [{"original": string, "corrected": string, "explanation_en": string}],\n'
        '  "overall_feedback_en": string (2-3 encouraging sentences in English)\n'
        "}"
    )
    user = f"Correct the grammar and spelling in this French text:\n\n{text}"
    return _chat_json(system, user)


def chat_reply(level: CEFRLevel, history: list[ChatMessage], message: str) -> dict:
    grammar_ref = _load_grammar_reference(level)
    system = (
        f"{_BASE_SYSTEM_PROMPT}\n"
        f"You are having a spoken conversation practice session with a {level} learner "
        f"({_LEVEL_DESCRIPTIONS[level]}). Keep replies short (1-3 sentences) and natural.\n"
        f"{grammar_ref}\n"
        "Respond with JSON matching exactly this schema:\n"
        '{"reply_fr": string, "reply_en": string (English translation of reply_fr)}'
    )
    transcript = "\n".join(f"{m.role}: {m.content}" for m in history)
    user = f"Conversation so far:\n{transcript}\n\nUser just said: \"{message}\"\nReply in French as the tutor."
    return _chat_json(system, user)
