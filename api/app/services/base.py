from abc import ABC, abstractmethod
 
 
class SpeechToTextService(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, filename: str) -> dict:
        """Transcribe audio and return structured result."""
        ...
 
 
class TextToSpeechService(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice_model: str, output_format: str) -> bytes:
        """Synthesize text and return raw audio bytes."""
        ...
 
 
class DocumentProcessingService(ABC):
    @abstractmethod
    async def analyze(self, image_bytes: bytes, filename: str) -> dict:
        """Analyze a document image and return structured extraction."""
        ...
 