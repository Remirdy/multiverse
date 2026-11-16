import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, Index
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

    turns = relationship(
        "ComparisonTurn",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ComparisonTurn.created_at",
    )


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
    status = Column(String(30), nullable=False, default="success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    turn = relationship("ComparisonTurn", back_populates="responses")


class ProviderConfigRecord(Base):
    __tablename__ = "provider_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    base_url = Column(String(512), nullable=False)
    is_local = Column(Boolean, default=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    capabilities_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class JobRecord(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_type = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="queued", index=True)
    progress_phase = Column(String(120), nullable=True)
    budget_json = Column(Text, nullable=True)
    usage_json = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    cancel_requested = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    events = relationship(
        "JobEventRecord",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="JobEventRecord.sequence",
    )


class JobEventRecord(Base):
    __tablename__ = "job_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    job = relationship("JobRecord", back_populates="events")

    __table_args__ = (Index("ix_job_events_job_seq", "job_id", "sequence"),)


class ArtifactRecord(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    media_type = Column(String(120), nullable=False)
    size_bytes = Column(Integer, nullable=False, default=0)
    content_hash = Column(String(64), nullable=False)
    storage_path = Column(String(512), nullable=False)
    origin_type = Column(String(64), nullable=False, default="upload")
    origin_id = Column(String(64), nullable=True, index=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)


class CouncilPresetRecord(Base):
    __tablename__ = "council_presets"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=False, default="")
    config_json = Column(Text, nullable=False)
    is_builtin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)


class CouncilSessionRecord(Base):
    __tablename__ = "council_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="queued", index=True)
    preset_id = Column(String(64), nullable=True)
    config_json = Column(Text, nullable=False)
    proposals_json = Column(Text, nullable=False, default="[]")
    reviews_json = Column(Text, nullable=False, default="[]")
    revisions_json = Column(Text, nullable=False, default="[]")
    verifications_json = Column(Text, nullable=False, default="[]")
    disagreements_json = Column(Text, nullable=False, default="[]")
    synthesis_json = Column(Text, nullable=True)
    usage_json = Column(Text, nullable=False, default="{}")
    job_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class WorkflowRecord(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False, default="")
    version = Column(Integer, nullable=False, default=1)
    graph_json = Column(Text, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class WorkflowRunRecord(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_version = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="queued", index=True)
    inputs_json = Column(Text, nullable=False, default="{}")
    node_states_json = Column(Text, nullable=False, default="{}")
    outputs_json = Column(Text, nullable=False, default="{}")
    usage_json = Column(Text, nullable=False, default="{}")
    job_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class StudyNotebookRecord(Base):
    __tablename__ = "study_notebooks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    course = Column(String(120), nullable=False, default="General")
    description = Column(Text, nullable=False, default="")
    tags_json = Column(Text, nullable=False, default="[]")
    notes_markdown = Column(Text, nullable=False, default="")
    formula_sheet_json = Column(Text, nullable=False, default="[]")
    mind_map_json = Column(Text, nullable=False, default="{}")
    sources_json = Column(Text, nullable=False, default="[]")
    saved_items_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class StudyAssignmentRecord(Base):
    __tablename__ = "study_assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    notebook_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    course = Column(String(120), nullable=False, default="General")
    mode = Column(String(48), nullable=False, default="step_by_step")
    artifact_id = Column(String(36), nullable=True)
    questions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class FlashcardDeckRecord(Base):
    __tablename__ = "flashcard_decks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    notebook_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    course = Column(String(120), nullable=False, default="General")
    cards_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class QuestionBankItemRecord(Base):
    __tablename__ = "question_bank_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    notebook_id = Column(String(36), nullable=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(32), nullable=False, default="short_answer")
    options_json = Column(Text, nullable=False, default="[]")
    correct_answer = Column(Text, nullable=False, default="")
    explanation = Column(Text, nullable=False, default="")
    difficulty = Column(String(24), nullable=False, default="medium")
    topic = Column(String(120), nullable=False, default="General")
    tags_json = Column(Text, nullable=False, default="[]")
    source_ref = Column(String(255), nullable=True)
    attempts_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
    needs_practice = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)


class ExamRecord(Base):
    __tablename__ = "study_exams"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    notebook_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    mode = Column(String(32), nullable=False, default="practice")
    time_limit_minutes = Column(Integer, nullable=True)
    questions_json = Column(Text, nullable=False, default="[]")
    attempts_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class StudyPlanRecord(Base):
    __tablename__ = "study_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    exam_date = Column(String(32), nullable=False)
    daily_hours = Column(Float, nullable=False, default=2.0)
    courses_json = Column(Text, nullable=False, default="[]")
    sessions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
