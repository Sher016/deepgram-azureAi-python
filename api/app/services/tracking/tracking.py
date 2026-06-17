import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request_log import ApiRequest, SttDetail, TtsDetail, IdpDetail


class RequestTracker:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _create_api_request(
        self,
        endpoint: str,
        http_status: int,
        latency_ms: int,
        error_msg: str | None = None,
    ) -> uuid.UUID:
        """Crea el registro base compartido y retorna el request_id."""
        request_id = uuid.uuid4()
        self._db.add(ApiRequest(
            request_id=request_id,
            endpoint=endpoint,
            http_status=http_status,
            latency_ms=latency_ms,
            error_msg=error_msg,
        ))
        await self._db.flush()
        return request_id

    async def log_stt(
        self,
        *,
        http_status: int,
        latency_ms: int,
        filename: str,
        stt_result: dict,
        error_msg: str | None = None,
    ) -> str:
        request_id = await self._create_api_request("stt", http_status, latency_ms, error_msg)
        self._db.add(SttDetail(
            request_id=request_id,
            input_filename=filename,
            audio_duration_secs=stt_result.get("audio_duration_secs", 0.0),
            audio_channels=stt_result.get("audio_channels", 1),
            detected_language=stt_result.get("detected_language"),
            deepgram_model=stt_result.get("deepgram_model"),
            num_speakers=stt_result.get("num_speakers"),
            transcript_summary=stt_result.get("transcript", "")[:500],
            diarization_json=stt_result.get("diarization", []),
            input_tokens=stt_result.get("input_tokens"),
            output_tokens=stt_result.get("output_tokens"),
        ))
        return str(request_id)

    async def log_tts(
        self,
        *,
        http_status: int,
        latency_ms: int,
        input_text: str,
        voice_model: str,
        output_format: str,
        error_msg: str | None = None,
        file_reference: str | None = None,
    ) -> str:
        request_id = await self._create_api_request("tts", http_status, latency_ms, error_msg)
        self._db.add(TtsDetail(
            request_id=request_id,
            input_text=input_text,
            input_chars=len(input_text),
            voice_model=voice_model,
            output_format=output_format,
            file_reference=file_reference,
        ))
        return str(request_id)

    async def log_idp(
        self,
        *,
        http_status: int,
        latency_ms: int,
        filename: str,
        idp_result: dict,
        error_msg: str | None = None,
    ) -> str:
        request_id = await self._create_api_request("idp", http_status, latency_ms, error_msg)
        self._db.add(IdpDetail(
            request_id=request_id,
            input_filename=filename,
            document_type=idp_result.get("document_type", "unknown"),
            prompt_tokens=idp_result.get("prompt_tokens", 0),
            completion_tokens=idp_result.get("completion_tokens", 0),
            total_tokens=idp_result.get("total_tokens", 0),
            azure_model=idp_result.get("azure_model", ""),
            extracted_json=idp_result.get("extracted_json"),
        ))
        return str(request_id)