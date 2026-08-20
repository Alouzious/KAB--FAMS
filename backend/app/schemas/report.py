from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel
from app.models.final_report import ReportStatus


class ProgressReportCreate(BaseModel):
    week_ending: date
    tasks_completed: str
    tasks_in_progress: str
    next_week_tasks: str
    problems_challenges: str | None = None


class ProgressReportOut(BaseModel):
    id: UUID
    student_id: UUID
    week_ending: date
    tasks_completed: str
    tasks_in_progress: str
    next_week_tasks: str
    problems_challenges: str | None
    supervisor_comments: str | None

    class Config:
        from_attributes = True


class ProgressReportComment(BaseModel):
    supervisor_comments: str


class FinalReportSubmit(BaseModel):
    file_url: str
    file_public_id: str | None = None


class FinalReportOut(BaseModel):
    id: UUID
    student_id: UUID
    file_url: str
    status: ReportStatus
    reviewer_notes: str | None
    submitted_at: datetime
    reviewed_at: datetime | None

    class Config:
        from_attributes = True


class FinalReportReview(BaseModel):
    status: ReportStatus
    reviewer_notes: str | None = None
