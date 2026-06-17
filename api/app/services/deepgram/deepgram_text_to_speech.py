import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError, handle_external_errors
from app.services.base import TextToSpeechService


class DeepgramTTSService(TextToSpeechService):
    def __init__(self) -> None:
        self._api_key = get_settings().deepgram_api_key
        self._tts_url = get_settings().deepgram_tts_url
        

    @handle_external_errors(service_name="Deepgram TTS")
    async def synthesize(self, text: str, voice_model: str, output_format: str) -> bytes:
        """
        Send text to Deepgram TTS and return raw audio bytes.
        """
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self._tts_url,
                params={"model": voice_model, "encoding": output_format},
                headers={
                    "Authorization": f"Token {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={"text": text},
            )

        if response.status_code != 200:
            raise ExternalServiceError(
                service="Deepgram TTS",
                detail=f"HTTP {response.status_code} — {response.text[:300]}",
            )

        return response.content