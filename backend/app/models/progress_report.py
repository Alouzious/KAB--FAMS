import uuid
from sqlalchemy import Column, String, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProgressReport(Base):
    __tablename__ = "progress_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)

    week_ending = Column(Date, nullable=False)  # must be a Friday, validate in schema
    tasks_completed = Column(Text, nullable=False)
    tasks_in_progress = Column(Text, nullable=False)
    next_week_tasks = Column(Text, nullable=False)
    problems_challenges = Column(Text, nullable=True)
    supervisor_comments = Column(Text, nullable=True)

    student = relationship("StudentProfile")