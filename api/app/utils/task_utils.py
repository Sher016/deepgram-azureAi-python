import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


async def create_task(
    db: AsyncSession,
    task_type: str,
    filename: str | None = None,
) -> str:
    """
    Create a new task and return its ID.
    """
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        type=task_type,
        status=TaskStatus.PENDING,
        filename=filename,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return str(task_id)


async def get_task(db: AsyncSession, task_id: str) -> Task | None:
    """
    Get a task by ID. Returns None if not found.
    """
    return await db.get(Task, task_id)


async def update_task_status(
    db: AsyncSession,
    task_id: str,
    status: TaskStatus,
    error_msg: str | None = None,
) -> None:
    """
    Update task status. Optionally set error message.
    """
    task = await db.get(Task, task_id)
    if task:
        task.status = status
        if error_msg:
            task.error_msg = error_msg
        await db.commit()


async def update_task_result(
    db: AsyncSession,
    task_id: str,
    result: dict,
) -> None:
    """
    Update task with successful result.
    """
    task = await db.get(Task, task_id)
    if task:
        task.status = TaskStatus.COMPLETED
        task.result = result
        await db.commit()


def build_task_response(task: Task) -> dict:
    """
    Build status response for a task.
    """
    return {
        "task_id": task.id,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def validate_file_extension(
    filename: str | None,
    allowed_extensions: set[str],
) -> None:
    """
    Validate file extension against allowed set.
    Raises HTTPException 400 if invalid.
    """
    ext = (filename or "").rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Accepted: {', '.join(allowed_extensions)}"
        )


def check_task_ready(task: Task) -> None:
    """
    Check if task is ready to return result.
    Raises HTTPException if still processing or failed.
    """
    if task.status == TaskStatus.PENDING or task.status == TaskStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Task is still {task.status}",
        )
    
    if task.status == TaskStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task failed: {task.error_msg}",
        )
        
async def wait_for_task_completion(
    db: AsyncSession,
    task_id: str,
    timeout: int = 60,
    check_interval: float = 0.5,
) -> Task:
    """
    Espera activamente a que una tarea termine.
    Retorna la tarea completada o lanza HTTPException.
    """
    import asyncio
    import time
    from fastapi import HTTPException
    from app.models.task import TaskStatus
    
    start = time.monotonic()
    
    while time.monotonic() - start < timeout:
        task = await get_task(db, task_id)
        
        if task.status == TaskStatus.COMPLETED:
            return task
        
        if task.status == TaskStatus.FAILED:
            raise HTTPException(500, detail=f"Task failed: {task.error_msg}")
        
        await asyncio.sleep(check_interval)
    
    raise HTTPException(408, detail="Request timeout")