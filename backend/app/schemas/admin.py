from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID

from app.core.security import is_valid_university_email


class CreateFacultyRequest(BaseModel):
    name: str


class CreateFacultyAdminRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    faculty_id: UUID

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not is_valid_university_email(v):
            raise ValueError("Only Kabale University (@kab.ac.ug) emails are allowed")
        return v.lower()


class CreateDepartmentRequest(BaseModel):
    name: str
    field_attachment_year: int = 3


class CreateDepartmentAdminRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    department_id: UUID

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not is_valid_university_email(v):
            raise ValueError("Only Kabale University (@kab.ac.ug) emails are allowed")
        return v.lower()


class CreateSupervisorRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str | None = None
    office: str | None = None
    # Required when a faculty_admin creates the supervisor (they must pick
    # which department in their faculty). Ignored for department_admin,
    # who is already scoped to one department.
    department_id: UUID | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not is_valid_university_email(v):
            raise ValueError("Only Kabale University (@kab.ac.ug) emails are allowed")
        return v.lower()


class AssignSupervisorRequest(BaseModel):
    student_id: UUID
    supervisor_id: UUID