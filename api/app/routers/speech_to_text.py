import asyncio

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_api_key
from app.core.database import get_db
from app.utils.queue import TaskPayload, enqueue, wait_for_task
from app.schemas.speech_to_text import SttResponse, SpeakerSegment, SpeechToTextId
from app.utils.task_utils import create_task, get_task, build_task_response, check_task_ready, validate_file_extension
from app.models.task import TaskStatus

ALLOWED_EXTENSIONS = {"mp3", "wav"}
router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])


@router.post("")
async def speech_to_text(
    file: UploadFile = File(...),
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> SttResponse:
    """
    Endpoint para la transcripción de archivos de audio. Acepta archivos en formato MP3 o WAV, devuelve la transcripción de audio con el lenguaje detectado y hablantes.
    """

    validate_file_extension(file.filename, ALLOWED_EXTENSIONS)

    task_id = await create_task(db, "stt", file.filename)
    audio_bytes = await file.read()
    event = asyncio.Event()

    enqueue(TaskPayload(
        task_id=task_id,
        task_type="stt",
        event=event,
        data={"audio_bytes": audio_bytes, "filename": file.filename or "audio"},
    ))

    completed = await wait_for_task(task_id, timeout=120)
    if not completed:
        raise HTTPException(status_code=408, detail="Request timeout processing audio.")

    task = await get_task(db, task_id)
    if task.status == TaskStatus.FAILED:
        raise HTTPException(status_code=502, detail=f"Processing failed: {task.error_msg}")

    result = task.result
    return SttResponse(
        request_id=task_id,
        transcript=result["transcript"],
        detected_language=result.get("detected_language"),
        audio_duration_secs=result["audio_duration_secs"],
        audio_channels=result["audio_channels"],
        deepgram_model=result.get("deepgram_model"),
        num_speakers=result.get("num_speakers"),
        diarization=[SpeakerSegment(**s) for s in result.get("diarization", [])],
    )



@router.post("/better_way")
async def speech_to_text_better_way(
        file: UploadFile = File(...),
        _: str = Depends(require_api_key),
        db: AsyncSession = Depends(get_db),
) -> SpeechToTextId:
    """
    Endpoint para la transcripción de archivos de audio. Acepta archivos en formato MP3 o WAV, devuelve el request_id para las futuras consultas del estado de una tarea.
    """

    validate_file_extension(file.filename, ALLOWED_EXTENSIONS)

    task_id = await create_task(db, "stt", file.filename)
    audio_bytes = await file.read()
    event = asyncio.Event()

    enqueue(TaskPayload(
        task_id=task_id,
        task_type="stt",
        event=event,
        data={"audio_bytes": audio_bytes, "filename": file.filename or "audio"},
    ))

    return  SpeechToTextId(
        task_id=task_id
    )

@router.get("/status/{task_id}")
async def get_stt_status(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Endpoint para consulta del status de una tarea de speech to text"""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return build_task_response(task)


@router.get("/result/{task_id}")
async def get_stt_result(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> SttResponse:
    """Endpoint para la consulta de la respuesta del speech to text"""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    check_task_ready(task)

    result = task.result
    return SttResponse(
        request_id=task_id,
        transcript=result["transcript"],
        detected_language=result.get("detected_language"),
        audio_duration_secs=result["audio_duration_secs"],
        audio_channels=result["audio_channels"],
        deepgram_model=result.get("deepgram_model"),
        num_speakers=result.get("num_speakers"),
        diarization=[SpeakerSegment(**s) for s in result.get("diarization", [])],
    )
