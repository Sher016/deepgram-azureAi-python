import asyncio

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_api_key
from app.core.database import get_db
from app.utils.queue import TaskPayload, enqueue, wait_for_task
from app.schemas.intelligence_document_processing import IdpResponse, TokenUsage, RequestIdResponse
from app.utils.task_utils import create_task, get_task, build_task_response, check_task_ready, validate_file_extension
from app.models.task import TaskStatus

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
router = APIRouter(prefix="/idp", tags=["Intelligent Document Processing"])


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> IdpResponse:

    """Endpoint para la extracción de información de cedulas devuelve la información de la cedula más la información de consumo"""
    validate_file_extension(file.filename, ALLOWED_EXTENSIONS)

    task_id = await create_task(db, "idp", file.filename)
    image_bytes = await file.read()
    event = asyncio.Event()

    enqueue(TaskPayload(
        task_id=task_id,
        task_type="idp",
        event=event,
        data={"image_bytes": image_bytes, "filename": file.filename or "document"},
    ))

    completed = await wait_for_task(task_id, timeout=60)
    if not completed:
        raise HTTPException(status_code=408, detail="Request timeout analyzing document.")

    task = await get_task(db, task_id)
    if task.status == TaskStatus.FAILED:
        raise HTTPException(status_code=502, detail=f"Processing failed: {task.error_msg}")

    result = task.result
    return IdpResponse(
        request_id=task_id,
        document_type=result["document_type"],
        azure_model=result["azure_model"],
        extracted_data=result["extracted_data"],
        token_usage=TokenUsage(
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            total_tokens=result["total_tokens"],
        ),
    )


@router.post("/analyze_better_way")
async def analyze_document_better_way(
        file: UploadFile = File(...),
        _: str = Depends(require_api_key),
        db: AsyncSession = Depends(get_db),
) -> RequestIdResponse:
    """Endpoint para la extracción de información de cedulas devuelve el id de la tarea para su posterior consulta"""
    validate_file_extension(file.filename, ALLOWED_EXTENSIONS)

    task_id = await create_task(db, "idp", file.filename)
    image_bytes = await file.read()
    event = asyncio.Event()

    enqueue(TaskPayload(
        task_id=task_id,
        task_type="idp",
        event=event,
        data={"image_bytes": image_bytes, "filename": file.filename or "document"},
    ))

    return RequestIdResponse(task_id=task_id)


@router.get("/status/{task_id}")
async def get_idp_status(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Endpoint para la consulta de tareas activas del extractor de cedulas"""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return build_task_response(task)


@router.get("/result/{task_id}")
async def get_idp_result(
    task_id: str,
    _: str = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> IdpResponse:
    """Endpoint para la consulta de respuestas del extractor de cedulas"""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    check_task_ready(task)

    result = task.result
    return IdpResponse(
        request_id=task_id,
        document_type=result["document_type"],
        azure_model=result["azure_model"],
        extracted_data=result["extracted_data"],
        token_usage=TokenUsage(
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            total_tokens=result["total_tokens"],
        ),
    )
