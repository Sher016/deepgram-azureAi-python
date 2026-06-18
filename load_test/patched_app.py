import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv("../infra/.env")

os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5434"

# Asegurar que el directorio `api` se encuentre en el path para que `app` pueda ser importado
api_path = Path(__file__).resolve().parent.parent / "api"
sys.path.append(str(api_path))

# Mocks
async def mock_stt_transcribe(self, audio_bytes, filename):
    await asyncio.sleep(0.5)
    return {
        "transcript": "Mock transcript result", 
        "detected_language": "es",
        "audio_duration_secs": 2.0, 
        "audio_channels": 1,
        "deepgram_model": "mock-model",
        "num_speakers": 1,
        "diarization": []
    }

async def mock_tts_synthesize(self, text, voice_model, output_format):
    await asyncio.sleep(0.5)
    return b"mocked_audio_bytes"

async def mock_idp_analyze(self, image_bytes, filename):
    await asyncio.sleep(0.5)
    return {
        "document_type": "cedula", 
        "azure_model": "mock-model", 
        "extracted_data": {"name": "Test Name", "id": "123456789"}, 
        "prompt_tokens": 10, 
        "completion_tokens": 10, 
        "total_tokens": 20
    }

# Parcheamos los métodos de las clases originales
patcher_stt = patch('app.services.deepgram.deepgram_speech_to_text.DeepgramSTTService.transcribe', mock_stt_transcribe)
patcher_tts = patch('app.services.deepgram.deepgram_text_to_speech.DeepgramTTSService.synthesize', mock_tts_synthesize)
patcher_idp = patch('app.services.azure_idp.azure_intelligence_document_processing.AzureIDPService.analyze', mock_idp_analyze)

# Parcheamos la función enqueue para que genere "trabajadores" concurrentes en lugar de usar una cola secuencial
def mock_enqueue(payload):
    import app.utils.queue
    import app.utils.worker
    import asyncio
    
    app.utils.queue.task_events[payload.task_id] = payload.event
    asyncio.create_task(app.utils.worker._dispatch(payload))

patcher_enqueue = patch('app.utils.queue.enqueue', mock_enqueue)

patcher_stt.start()
patcher_tts.start()
patcher_idp.start()
patcher_enqueue.start()

from app.main import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Corremos uvicorn pasándole la instancia directamente
    uvicorn.run(app, host="0.0.0.0", port=8001, workers=1)
