from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class PlacementCreate(BaseModel):
    organisation_id: UUID | None = None
    organisation_name: str
    organisation_email: str | None = None
    district: str | None = None
    address: str | None = None


class PlacementOut(BaseModel):
    id: UUID
    student_id: UUID
    organisation_id: UUID | None
    organisation_name: str
    organisation_email: str | None
    district: str | None
    address: str | None
    placement_letter_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
