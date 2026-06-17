import uuid  
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON, ForeignKey  
from app.core.database import Base


class ApiRequest(Base):
    """Tabla: api_requests - Guarda información general de cada petición"""
    __tablename__ = "api_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)  
    endpoint = Column(String(20))  
    http_status = Column(Integer)
    latency_ms = Column(Integer)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SttDetail(Base):
    """Tabla: stt_details - Guarda detalles específicos de STT"""
    __tablename__ = "stt_details"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("api_requests.request_id"), index=True)  
    input_filename = Column(String(255))
    audio_duration_secs = Column(Float)
    audio_channels = Column(Integer)
    detected_language = Column(String(10), nullable=True)
    deepgram_model = Column(String(50), nullable=True)
    num_speakers = Column(Integer, nullable=True)
    transcript_summary = Column(Text, nullable=True)
    diarization_json = Column(JSON, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)  


class TtsDetail(Base):
    """Tabla: tts_details - Guarda detalles específicos de TTS"""
    __tablename__ = "tts_details"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("api_requests.request_id"), index=True)  
    input_text = Column(Text)
    input_chars = Column(Integer)
    voice_model = Column(String(50))
    output_format = Column(String(10))
    file_reference = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)  


class IdpDetail(Base):
    """Tabla: idp_details - Guarda detalles específicos de IDP"""
    __tablename__ = "idp_details"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("api_requests.request_id"), index=True)  
    input_filename = Column(String(255))
    document_type = Column(String(50))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    azure_model = Column(String(50))
    extracted_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)  