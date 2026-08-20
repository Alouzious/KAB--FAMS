import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)

    departments = relationship("Department", back_populates="faculty")


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculties.id"), nullable=False)

    # Minimum year of study a student must reach before they're eligible
    # for field attachment in this department. Admin-configurable.
    field_attachment_year = Column(Integer, nullable=False, default=3)

    faculty = relationship("Faculty", back_populates="departments")