from fastapi import HTTPException, status
from app.models.task import Task, TaskStatus


def check_task_ready(task: Task) -> dict:
    """
    Check if task is ready and return appropriate response.
    Raises HTTPException if not ready or failed.
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
    
    return {"ready": True}


async def get_task_or_404(db, task_id: str) -> Task:
    """
    Get task or raise 404.
    """
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task