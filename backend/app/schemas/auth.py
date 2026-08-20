from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID

from app.core.security import is_valid_university_email


class StudentRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    faculty_id: UUID
    department_id: UUID
    year_of_study: int

    @field_validator("email")
    @classmethod
    def validate_university_email(cls, v: str) -> str:
        if not is_valid_university_email(v):
            raise ValueError("Only Kabale University (@kab.ac.ug) emails are allowed")
        return v.lower()

    @field_validator("year_of_study")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v < 1 or v > 6:
            raise ValueError("year_of_study must be between 1 and 6")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    is_eligible_for_fa: bool | None = None