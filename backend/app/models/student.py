import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    registration_number = Column(String, nullable=True)   # e.g. 2024/AKCS/5193/GF
    admission_year = Column(Integer, nullable=True)        # auto-suggested from email
    year_of_study = Column(Integer, nullable=False)        # student-selected, e.g. 1-4

    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculties.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)

    is_eligible_for_fa = Column(Boolean, default=False)  # computed at registration/update

    user = relationship("User", back_populates="student_profile")
    faculty = relationship("Faculty")
    department = relationship("Department")