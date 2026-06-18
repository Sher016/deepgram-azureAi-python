from pydantic import BaseModel

class SpeechToTextId(BaseModel):
    task_id: str

class SpeakerSegment(BaseModel):
    speaker: int
    start: float
    end: float
    text: str


class SttResponse(BaseModel):
    request_id: str
    transcript: str
    detected_language: str | None
    audio_duration_secs: float
    audio_channels: int
    deepgram_model: str | None
    num_speakers: int | None
    diarization: list[SpeakerSegment]
    utterances: list[dict] | None = None
    sentiment: dict | None = None
    topics: dict | None = None
    filler_words: list[dict] | None = None
 