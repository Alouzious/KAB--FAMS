import uuid
import enum
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class PageSlug(str, enum.Enum):
    GUIDELINES = "guidelines"
    FAQ = "faq"


class ContentPage(Base):
    """
    Editable long-form content — Guidelines, FAQ, etc — managed by
    super_admin so it never needs a code deploy to update.
    """
    __tablename__ = "content_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(Enum(PageSlug), nullable=False, unique=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)  # markdown or HTML, rendered on frontend

    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())