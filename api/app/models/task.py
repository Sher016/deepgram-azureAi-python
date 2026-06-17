from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, JSON
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID


class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(20)) 
    status = Column(String(20), default=TaskStatus.PENDING)
    filename = Column(String(255), nullable=True)
    result = Column(JSON, nullable=True)
    error_msg = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)