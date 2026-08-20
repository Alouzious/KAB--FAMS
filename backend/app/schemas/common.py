from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class MessageResponse(BaseModel):
    detail: str


class FacultyOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class DepartmentOut(BaseModel):
    id: str
    name: str
    faculty_id: str
    field_attachment_year: int

    class Config:
        from_attributes = True