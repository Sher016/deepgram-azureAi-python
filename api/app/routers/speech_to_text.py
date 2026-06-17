import asyncio

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_api_key
from app.core.database import get_db
from app.utils.queue import TaskPayload, enqueue, wait_for_task
from app.schemas.speech_to_text import SttResponse, SpeakerSegment
from app.utils.task_utils import create_task, get_task, build_task_response, check_task_ready, validate_file_extension
from app.models.task import TaskStatus

ALLOWED_EXTENSIONS = {"mp3", "wav"}
router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])


@router.post("", response_model=SttResponse, status_code=status.HTTP_200_OK, summary="Transcribe audio file")
async def speech_to_text(
    file: UploadFile = File(...),
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> SttResponse:
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


@router.get("/status/{task_id}", summary="Check STT task status")
async def get_stt_status(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return build_task_response(task)


@router.get("/result/{task_id}", response_model=SttResponse, summary="Get STT task result")
async def get_stt_result(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> SttResponse:
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
