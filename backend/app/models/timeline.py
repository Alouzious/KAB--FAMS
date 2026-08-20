import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TimelineEntry(Base):
    """University-wide field attachment calendar — super_admin managed."""
    __tablename__ = "timeline_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity = Column(String, nullable=False)          # e.g. "Deadline for uploading placement letter"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    academic_year = Column(String, nullable=False)      # e.g. "2025/2026"

    # NOTE: "Remark" (On Schedule / Overdue) is intentionally NOT stored —
    # it's computed at request time by comparing today's date to end_date.
    # See schemas/timeline.py for the computed property.