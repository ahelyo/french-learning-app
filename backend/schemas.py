from typing import Literal

from pydantic import BaseModel

CEFRLevel = Literal["A1", "A2", "B1", "B2"]
StoryLength = Literal["short", "medium", "long"]


class StoryRequest(BaseModel):
    level: CEFRLevel
    theme: str
    length: StoryLength = "short"


class VocabItem(BaseModel):
    french: str
    english: str


class StoryResponse(BaseModel):
    title_fr: str
    title_en: str
    story_fr: str
    story_en: str
    vocabulary: list[VocabItem]
    grammar_notes: list[str]
    level: CEFRLevel
    theme: str
    length: StoryLength
    audio_url: str


class LibraryStoryItem(BaseModel):
    cache_key: str
    level: CEFRLevel
    length: StoryLength
    theme: str
    title_fr: str
    title_en: str


class StoryCreateRequest(BaseModel):
    level: CEFRLevel
    length: StoryLength = "short"
    theme: str = ""
    title_fr: str
    title_en: str = ""
    story_fr: str
    story_en: str = ""
    vocabulary: list[VocabItem] = []
    grammar_notes: list[str] = []


class WritingCorrectionRequest(BaseModel):
    text: str
    level: CEFRLevel = "B1"


class CorrectionItem(BaseModel):
    original: str
    corrected: str
    explanation_en: str


class WritingCorrectionResponse(BaseModel):
    corrected_text: str
    corrections: list[CorrectionItem]
    overall_feedback_en: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatTextRequest(BaseModel):
    level: CEFRLevel
    history: list[ChatMessage] = []
    message: str


class ChatTextResponse(BaseModel):
    reply_fr: str
    reply_en: str


class ChatVoiceResponse(BaseModel):
    transcript_fr: str
    reply_fr: str
    reply_en: str
    audio_url: str
