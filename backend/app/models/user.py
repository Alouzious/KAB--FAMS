import uuid
import enum
from sqlalchemy import Column, String, Boolean, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    FACULTY_ADMIN = "faculty_admin"
    DEPARTMENT_ADMIN = "department_admin"
    SUPERVISOR = "supervisor"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # created_by tracks who created this account — null only for the
    # very first super_admin, seeded manually
    created_by = Column(UUID(as_uuid=True), nullable=True)

    student_profile = relationship(
        "StudentProfile", back_populates="user", uselist=False, cascade="all, delete"
    )
    admin_profile = relationship(
        "AdminProfile", back_populates="user", uselist=False, cascade="all, delete"
    )
    supervisor_profile = relationship(
        "SupervisorProfile", back_populates="user", uselist=False, cascade="all, delete"
    )