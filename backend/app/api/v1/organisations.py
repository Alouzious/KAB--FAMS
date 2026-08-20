from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.api.deps import require_role, get_current_user
from app.models.user import User, UserRole
from app.models.organisation import Organisation
from app.models.internship_opportunity import InternshipOpportunity, IncentiveType
from app.services.rating_service import submit_rating
from app.schemas.public import (
    OrganisationOut, OrganisationRatingCreate,
    InternshipOpportunityOut, InternshipOpportunityCreate,
)

router = APIRouter(tags=["organisations"])


# ---------- PARTNER ORGANISATIONS (public read) ----------
@router.get("/organisations", response_model=list[OrganisationOut])
def list_organisations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Organisation).order_by(Organisation.name).all()


@router.post("/organisations/rate", dependencies=[Depends(require_role(UserRole.STUDENT))])
def rate_organisation(
    payload: OrganisationRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not (1 <= payload.score <= 5):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "score must be between 1 and 5")

    organisation = db.query(Organisation).filter(Organisation.id == payload.organisation_id).first()
    if not organisation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organisation not found")

    updated = submit_rating(
        db, payload.organisation_id, current_user.student_profile.id, payload.score, payload.comment
    )
    return {"detail": "Rating submitted", "new_average": updated.rating_average}


# ---------- INTERNSHIP OPPORTUNITIES ----------
@router.get("/internship-opportunities", response_model=list[InternshipOpportunityOut])
def list_opportunities(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    opportunities = db.query(InternshipOpportunity).order_by(InternshipOpportunity.date_posted.desc()).all()
    return [
        InternshipOpportunityOut(
            id=str(o.id), organisation_name=o.organisation_name, district=o.district,
            intern_attributes=o.intern_attributes, incentive_type=o.incentive_type.value,
            num_slots=o.num_slots, contact_person=o.contact_person,
            contact_email=o.contact_email, contact_phone=o.contact_phone, date_posted=o.date_posted,
        )
        for o in opportunities
    ]


@router.post(
    "/internship-opportunities",
    response_model=InternshipOpportunityOut,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.DEPARTMENT_ADMIN))],
)
def create_opportunity(
    payload: InternshipOpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opportunity = InternshipOpportunity(
        organisation_name=payload.organisation_name,
        district=payload.district,
        intern_attributes=payload.intern_attributes,
        incentive_type=IncentiveType(payload.incentive_type),
        num_slots=payload.num_slots,
        contact_person=payload.contact_person,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        date_posted=date.today(),
        posted_by=current_user.id,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return InternshipOpportunityOut(
        id=str(opportunity.id), organisation_name=opportunity.organisation_name,
        district=opportunity.district, intern_attributes=opportunity.intern_attributes,
        incentive_type=opportunity.incentive_type.value, num_slots=opportunity.num_slots,
        contact_person=opportunity.contact_person, contact_email=opportunity.contact_email,
        contact_phone=opportunity.contact_phone, date_posted=opportunity.date_posted,
    )