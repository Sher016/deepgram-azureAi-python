from pydantic import BaseModel, Field
 
 
class TtsRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text to synthesize")
    voice_model: str = Field(
        default="aura-2-aquila-es",
        description="Deepgram voice model (e.g. aura-asteria-en, aura-zeus-en)",
    )
    output_format: str = Field(
        default="mp3",
        description="Audio output format: mp3 or wav",
        pattern="^(mp3|wav)$",
    )
 