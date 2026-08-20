from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_eligible_student, require_role
from app.models.user import User, UserRole
from app.models.placement import Placement
from app.schemas.placement import PlacementCreate, PlacementOut

router = APIRouter(prefix="/placements", tags=["placements"])


@router.post("/", response_model=PlacementOut, dependencies=[Depends(require_eligible_student)])
def create_placement(
    payload: PlacementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Placement).filter(Placement.student_id == current_user.student_profile.id).first()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Placement already recorded for this student")

    placement = Placement(student_id=current_user.student_profile.id, **payload.model_dump())
    db.add(placement)
    db.commit()
    db.refresh(placement)
    return placement


@router.get("/me", response_model=PlacementOut, dependencies=[Depends(require_role(UserRole.STUDENT))])
def my_placement(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    placement = db.query(Placement).filter(Placement.student_id == current_user.student_profile.id).first()
    if not placement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No placement recorded yet")
    return placement


@router.get(
    "/student/{student_id}",
    response_model=PlacementOut,
    dependencies=[Depends(require_role(UserRole.SUPERVISOR, UserRole.DEPARTMENT_ADMIN, UserRole.FACULTY_ADMIN))],
)
def student_placement(student_id: str, db: Session = Depends(get_db)):
    placement = db.query(Placement).filter(Placement.student_id == student_id).first()
    if not placement:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No placement found")
    return placement
