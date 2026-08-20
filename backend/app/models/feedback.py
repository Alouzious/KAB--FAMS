import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)

    process_feedback = Column(Text, nullable=True)  # "How would you improve the FA process?"
    system_feedback = Column(Text, nullable=True)    # "How would you improve KAB-FAMS?"

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("StudentProfile")