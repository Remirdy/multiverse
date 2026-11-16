import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Comparison")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    turns = relationship("ComparisonTurn", back_populates="conversation", cascade="all, delete-orphan", order_by="ComparisonTurn.created_at")

class ComparisonTurn(Base):
    __tablename__ = "comparison_turns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="turns")
    responses = relationship("ModelResponseRecord", back_populates="turn", cascade="all, delete-orphan")

class ModelResponseRecord(Base):
    __tablename__ = "model_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    turn_id = Column(String(36), ForeignKey("comparison_turns.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String(120), nullable=False)
    model_name = Column(String(120), nullable=False)
    provider = Column(String(60), nullable=False, default="NVIDIA NIM")
    response_text = Column(Text, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="success") # success, error, timeout
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    turn = relationship("ComparisonTurn", back_populates="responses")
