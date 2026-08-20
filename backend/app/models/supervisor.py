import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SupervisorProfile(Base):
    __tablename__ = "supervisor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    office = Column(String, nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)

    user = relationship("User", back_populates="supervisor_profile")
    department = relationship("Department")


class FieldSupervisor(Base):
    """External, non-login field supervisor contact tied to a placement."""
    __tablename__ = "field_supervisors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)

    student = relationship("StudentProfile")


class SupervisorAssignment(Base):
    """Links one academic supervisor to one student. One supervisor per student."""
    __tablename__ = "supervisor_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False, unique=True)
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey("supervisor_profiles.id"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    student = relationship("StudentProfile")
    supervisor = relationship("SupervisorProfile")