import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Placement(Base):
    __tablename__ = "placements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False, unique=True)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=True)

    # kept even if organisation isn't in the partner directory
    organisation_name = Column(String, nullable=False)
    organisation_email = Column(String, nullable=True)
    district = Column(String, nullable=True)
    address = Column(String, nullable=True)

    placement_letter_url = Column(String, nullable=True)  # Cloudinary URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("StudentProfile")