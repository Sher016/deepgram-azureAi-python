import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskPayload:
    """Representa una tarea encolada con todo lo necesario para procesarla."""
    task_id: str
    task_type: str 
    event: asyncio.Event  
    data: dict[str, Any] = field(default_factory=dict)



task_queue: asyncio.Queue[TaskPayload] = asyncio.Queue()


task_events: dict[str, asyncio.Event] = {}


def enqueue(payload: TaskPayload) -> None:
    """Registra el evento y encola la tarea."""
    task_events[payload.task_id] = payload.event
    task_queue.put_nowait(payload)


async def wait_for_task(task_id: str, timeout: int) -> bool:
    """
    El router llama esto para esperar a que el worker termine.
    Retorna True si completó, False si hizo timeout.
    """
    event = task_events.get(task_id)
    if not event:
        return False
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        return False
    finally:
        task_events.pop(task_id, None)