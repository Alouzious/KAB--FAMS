import uuid
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    district = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # Computed/cached from OrganisationRating entries — updated whenever
    # a new rating is submitted, avoids recalculating on every page load
    rating_average = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=False, default=0)