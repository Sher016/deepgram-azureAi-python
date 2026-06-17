import asyncio
import logging
import time

from app.utils.queue import task_queue, TaskPayload

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    """
    Worker global que corre indefinidamente consumiendo la cola.
    Se lanza una sola vez al iniciar la app vía lifespan.
    """
    logger.info("Worker started, waiting for tasks...")
    while True:
        payload = await task_queue.get()
        try:
            await _dispatch(payload)
        except Exception as exc:
            logger.exception("Unhandled error on task %s: %s", payload.task_id, exc)
        finally:
            task_queue.task_done()


async def _dispatch(payload: TaskPayload) -> None:
    handlers = {
        "stt": _handle_stt,
        "tts": _handle_tts,
        "idp": _handle_idp,
    }
    handler = handlers.get(payload.task_type)
    if handler is None:
        logger.error("Unknown task type: %s", payload.task_type)
        payload.event.set()  
        return

    await handler(payload)


async def _handle_stt(payload: TaskPayload) -> None:
    from app.core.database import AsyncSessionLocal
    from app.services.deepgram.deepgram_speech_to_text import DeepgramSTTService
    from app.services.tracking.tracking import RequestTracker
    from app.utils.task_utils import update_task_status, update_task_result
    from app.models.task import TaskStatus
    

    task_id = payload.task_id
    audio_bytes: bytes = payload.data["audio_bytes"]
    filename: str = payload.data["filename"]
    

    async with AsyncSessionLocal() as db:
        try:
            await update_task_status(db, task_id, TaskStatus.PROCESSING)

            start = time.monotonic()
            result = await DeepgramSTTService().transcribe(audio_bytes, filename)
            latency_ms = int((time.monotonic() - start) * 1000)

            await update_task_result(db, task_id, result)
            await RequestTracker(db).log_stt(
                http_status=200,
                latency_ms=latency_ms,
                filename=filename,
                stt_result=result,
            )
            
            sys.stdout.write(f"✅ Result: {result.get('transcript')[:100]}\n")
            sys.stdout.flush()
            await db.commit()
            logger.info("STT task %s completed in %dms", task_id, latency_ms)

        except Exception as exc:
            await update_task_status(db, task_id, TaskStatus.FAILED, str(exc))
            await db.commit()
            logger.error("STT task %s failed: %s", task_id, exc)

        finally:
            payload.event.set()  # despierta al router 


async def _handle_tts(payload: TaskPayload) -> None:
    from app.core.database import AsyncSessionLocal
    from app.services.deepgram.deepgram_text_to_speech import DeepgramTTSService
    from app.services.tracking.tracking import RequestTracker
    from app.utils.task_utils import update_task_status, update_task_result
    from app.models.task import TaskStatus

    task_id = payload.task_id
    text: str = payload.data["text"]
    voice_model: str = payload.data["voice_model"]
    output_format: str = payload.data["output_format"]

    async with AsyncSessionLocal() as db:
        try:
            await update_task_status(db, task_id, TaskStatus.PROCESSING)

            start = time.monotonic()
            audio_bytes = await DeepgramTTSService().synthesize(text, voice_model, output_format)
            latency_ms = int((time.monotonic() - start) * 1000)

            await update_task_result(db, task_id, {
                "audio_bytes": audio_bytes.hex(),
                "output_format": output_format,
            })
            await RequestTracker(db).log_tts(
                http_status=200,
                latency_ms=latency_ms,
                input_text=text,
                voice_model=voice_model,
                output_format=output_format,
            )
            await db.commit()
            logger.info("TTS task %s completed in %dms", task_id, latency_ms)

        except Exception as exc:
            await update_task_status(db, task_id, TaskStatus.FAILED, str(exc))
            await db.commit()
            logger.error("TTS task %s failed: %s", task_id, exc)

        finally:
            payload.event.set()


async def _handle_idp(payload: TaskPayload) -> None:
    from app.core.database import AsyncSessionLocal
    from app.services.llm.llm import get_llm
    from app.services.azure_idp.azure_intelligence_document_processing import AzureIDPService
    from app.services.tracking.tracking import RequestTracker
    from app.utils.task_utils import update_task_status, update_task_result
    from app.models.task import TaskStatus

    task_id = payload.task_id
    image_bytes: bytes = payload.data["image_bytes"]
    filename: str = payload.data["filename"]

    async with AsyncSessionLocal() as db:
        try:
            await update_task_status(db, task_id, TaskStatus.PROCESSING)

            start = time.monotonic()
            result = await AzureIDPService(llm=get_llm()).analyze(image_bytes, filename)
            latency_ms = int((time.monotonic() - start) * 1000)

            await update_task_result(db, task_id, result)
            await RequestTracker(db).log_idp(
                http_status=200,
                latency_ms=latency_ms,
                filename=filename,
                idp_result=result,
            )
            await db.commit()
            logger.info("IDP task %s completed in %dms", task_id, latency_ms)

        except Exception as exc:
            await update_task_status(db, task_id, TaskStatus.FAILED, str(exc))
            await db.commit()
            logger.error("IDP task %s failed: %s", task_id, exc)

        finally:
            payload.event.set()