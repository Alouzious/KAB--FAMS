from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.organisation import Organisation
from app.models.organisation_rating import OrganisationRating


def submit_rating(db: Session, organisation_id, student_id, score: int, comment: str | None) -> Organisation:
    rating = OrganisationRating(
        organisation_id=organisation_id,
        student_id=student_id,
        score=score,
        comment=comment,
    )
    db.add(rating)
    db.flush()

    # Recalculate cached average/count on the Organisation itself,
    # so listing organisations doesn't need to aggregate on every read
    agg = db.query(
        func.avg(OrganisationRating.score),
        func.count(OrganisationRating.id),
    ).filter(OrganisationRating.organisation_id == organisation_id).first()

    organisation = db.query(Organisation).filter(Organisation.id == organisation_id).first()
    organisation.rating_average = round(float(agg[0]), 2) if agg[0] else None
    organisation.rating_count = agg[1] or 0

    db.commit()
    db.refresh(organisation)
    return organisation