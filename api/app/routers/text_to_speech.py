import asyncio

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_api_key
from app.core.database import get_db
from app.utils.queue import TaskPayload, enqueue, wait_for_task
from app.schemas.text_to_speech import TtsRequest
from app.utils.task_utils import create_task, get_task, build_task_response, check_task_ready
from app.models.task import TaskStatus

AUDIO_MEDIA_TYPES = {"mp3": "audio/mpeg", "wav": "audio/wav"}
router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


@router.post("", status_code=status.HTTP_200_OK, summary="Synthesize text to audio")
async def text_to_speech(
    body: TtsRequest,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> Response:
    task_id = await create_task(db, "tts")
    event = asyncio.Event()

    enqueue(TaskPayload(
        task_id=task_id,
        task_type="tts",
        event=event,
        data={"text": body.text, "voice_model": body.voice_model, "output_format": body.output_format},
    ))

    completed = await wait_for_task(task_id, timeout=60)
    if not completed:
        raise HTTPException(status_code=408, detail="Request timeout synthesizing audio.")

    task = await get_task(db, task_id)
    if task.status == TaskStatus.FAILED:
        raise HTTPException(status_code=502, detail=f"Processing failed: {task.error_msg}")

    result = task.result
    audio_bytes = bytes.fromhex(result["audio_bytes"])
    output_format = result.get("output_format", "mp3")
    media_type = AUDIO_MEDIA_TYPES.get(output_format, "audio/mpeg")

    return Response(
        content=audio_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="tts_output.{output_format}"'},
    )


@router.get("/status/{task_id}", summary="Check TTS task status")
async def get_tts_status(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return build_task_response(task)


@router.get("/result/{task_id}", summary="Download synthesized audio")
async def get_tts_result(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> Response:
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    check_task_ready(task)

    result = task.result
    audio_bytes = bytes.fromhex(result["audio_bytes"])
    output_format = result.get("output_format", "mp3")
    media_type = AUDIO_MEDIA_TYPES.get(output_format, "audio/mpeg")

    return Response(
        content=audio_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="tts_output.{output_format}"'},
    )