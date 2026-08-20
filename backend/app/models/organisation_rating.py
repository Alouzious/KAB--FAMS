import uuid
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrganisationRating(Base):
    """
    Post-attachment rating from a student who was placed at this
    organisation. Feeds Organisation.rating_average / rating_count.
    """
    __tablename__ = "organisation_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)

    score = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organisation = relationship("Organisation")
    student = relationship("StudentProfile")