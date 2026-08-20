import uuid
import enum
from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClockType(str, enum.Enum):
    IN = "in"
    OUT = "out"


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)

    clock_type = Column(Enum(ClockType), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy_meters = Column(Float, nullable=True)
    approximate_location = Column(String, nullable=True)  # reverse-geocoded address
    remarks = Column(String, nullable=True)
    device = Column(String, nullable=True)  # "Android" / "iOS" / "Web"

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("StudentProfile")