import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReportStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"  # e.g. needs revision


class FinalReport(Base):
    __tablename__ = "final_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False, unique=True)

    file_url = Column(String, nullable=False)       # Cloudinary URL
    file_public_id = Column(String, nullable=True)   # Cloudinary public_id, useful for replace/delete

    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.SUBMITTED)
    reviewer_notes = Column(String, nullable=True)   # academic supervisor's notes on the report

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    student = relationship("StudentProfile")