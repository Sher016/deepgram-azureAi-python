from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
   
    from app.core.config import get_settings
    get_settings()

 
    from app.core.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

  
    import asyncio
    from app.utils.worker import run_worker
    worker_task = asyncio.create_task(run_worker())

    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Technical Assessment API",
        version="1.0.0",
        lifespan=lifespan,
    )

    from app.routers.speech_to_text import router as speech_router
    from app.routers.text_to_speech import router as tts_router
    from app.routers.intelligence_document_processing import router as idp_router
    
    app.include_router(speech_router)
    app.include_router(tts_router)
    app.include_router(idp_router)

    return app


app = create_app()
 
 

