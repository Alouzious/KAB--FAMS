import uuid
import enum
from sqlalchemy import Column, Float, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ResultStatus(str, enum.Enum):
    DRAFT = "draft"                # supervisor has started scoring
    SUBMITTED = "submitted"        # supervisor finalized their score
    COMPILED = "compiled"          # department admin compiled into dept results
    RELEASED = "released"          # visible to student


class Result(Base):
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False, unique=True)
    graded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # academic supervisor

    # Kept flexible: raw scores per component, final score computed separately
    field_supervisor_score = Column(Float, nullable=True)   # from sealed Form B, entered by supervisor
    academic_supervisor_score = Column(Float, nullable=True)  # from final report review
    final_score = Column(Float, nullable=True)               # combined/weighted total
    grade_letter = Column(String, nullable=True)             # e.g. "A", "B+", computed from final_score

    status = Column(Enum(ResultStatus), nullable=False, default=ResultStatus.DRAFT)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("StudentProfile")