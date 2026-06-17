import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError, handle_external_errors
from app.services.base import SpeechToTextService
from app.utils.diarization import build_speaker_segments
from app.utils.file_utils import resolve_content_type


_QUERY_PARAMS = {
    "model": "nova-3",
    "diarize": "true",
    "punctuate": "true",
    "smart_format": "true",
    "detect_language": "true",
    "sentiment": "true",  
    "topics": "true",
    "numerals": "true",      
    "filler_words": "true",     
    "utterances": "true", 
}
 

class DeepgramSTTService(SpeechToTextService):
    def __init__(self) -> None:
        self._api_key = get_settings().deepgram_api_key

    @handle_external_errors(service_name="Deepgram STT")
    async def transcribe(self, audio_bytes: bytes, filename: str) -> dict:
        
        settings = get_settings()
        content_type = resolve_content_type(filename, default="audio/mpeg")

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                settings.deepgram_stt_url,
                params=_QUERY_PARAMS,
                headers={
                    "Authorization": f"Token {self._api_key}",
                    "Content-Type": content_type,
                },
                content=audio_bytes,
            )

        if response.status_code != 200:
            raise ExternalServiceError(
                service="Deepgram STT",
                detail=f"HTTP {response.status_code} — {response.text[:300]}",
            )

        return self._parse_response(response.json())

    @staticmethod
    def _parse_response(data: dict) -> dict:
        

        metadata = data.get("metadata", {})
        results = data.get("results", {})
        # channels = data.get("results", {}).get("channels", [{}])
        channels = results.get("channels", [{}])
        first_channel = channels[0] if channels else {}
        alternatives = first_channel.get("alternatives", [{}])
        best = alternatives[0] if alternatives else {}

        
        words = best.get("words", [])
        segments = build_speaker_segments(words)
        speakers = {w.get("speaker") for w in words if w.get("speaker") is not None}

        model_info = metadata.get("model_info", {})
        first_model = next(iter(model_info.values())) if model_info else {}
        model_name = first_model.get("name")

        summary_info = metadata.get("summary_info", {})
        input_tokens = summary_info.get("input_tokens")
        output_tokens = summary_info.get("output_tokens")
        
        return {
            "transcript": best.get("transcript", ""),
            "detected_language": first_channel.get("detected_language"),
            "audio_duration_secs": metadata.get("duration", 0.0),
            "audio_channels": metadata.get("channels", 1),
            "deepgram_model": model_name,
            "num_speakers": len(speakers) if speakers else None,
            "diarization": segments,
            "utterances": results.get("utterances", []),          
            "sentiment": results.get("sentiments", {}),             
            "topics": results.get("topics", {}),                   
            "filler_words": [                
                w for w in words if w.get("word", "").lower() in ["eh", "um", "ah", "uh"]
            ],
        }