import uuid
import enum
from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class IncentiveType(str, enum.Enum):
    NO_INCENTIVE = "intern_given_no_incentive"
    PAYS_FOR_INTERNSHIP = "intern_pays_for_internship"
    STIPEND_PROVIDED = "intern_given_stipend"


class InternshipOpportunity(Base):
    """
    Admin-entered opportunities (v1: admin enters on organisation's behalf,
    no separate organisation login yet — matches your decision to keep
    this simple for the first version).
    """
    __tablename__ = "internship_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=True)

    organisation_name = Column(String, nullable=False)  # kept even if not linked to Organisation
    district = Column(String, nullable=True)
    intern_attributes = Column(String, nullable=True)    # e.g. "Knowledge of PHP, MYSQL, HTML"
    incentive_type = Column(Enum(IncentiveType), nullable=False, default=IncentiveType.NO_INCENTIVE)
    num_slots = Column(Integer, nullable=False, default=1)
    contact_person = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    date_posted = Column(Date, nullable=False)
    posted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    organisation = relationship("Organisation")