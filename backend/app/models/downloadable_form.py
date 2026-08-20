import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class DownloadableForm(Base):
    """
    Admin-uploaded PDF templates: Form B, Report Template, Logbook,
    Weekly Progress Report form. super_admin managed, so files can be
    replaced without a redeploy.
    """
    __tablename__ = "downloadable_forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)         # e.g. "Form B - Field Supervisor Assessment form"
    file_url = Column(String, nullable=False)     # Cloudinary URL
    file_public_id = Column(String, nullable=True)

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())