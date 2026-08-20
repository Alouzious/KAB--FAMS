from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.attendance import ClockType


class ClockRequest(BaseModel):
    clock_type: ClockType
    latitude: float | None = None
    longitude: float | None = None
    accuracy_meters: float | None = None
    approximate_location: str | None = None
    remarks: str | None = None
    device: str | None = None


class AttendanceLogOut(BaseModel):
    id: UUID
    student_id: UUID
    clock_type: ClockType
    latitude: float | None
    longitude: float | None
    approximate_location: str | None
    remarks: str | None
    device: str | None
    timestamp: datetime

    class Config:
        from_attributes = True
