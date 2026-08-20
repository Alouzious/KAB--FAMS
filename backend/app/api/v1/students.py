from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import Faculty, Department
from app.services.eligibility_service import check_eligibility
from app.schemas.common import FacultyOut, DepartmentOut
from app.schemas.public import UpdateYearOfStudy

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/faculties", response_model=list[FacultyOut])
def list_faculties(db: Session = Depends(get_db)):
    return db.query(Faculty).all()


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(faculty_id: str, db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.faculty_id == faculty_id).all()


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    profile = current_user.student_profile
    return {
        "email": current_user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "year_of_study": profile.year_of_study,
        "faculty": profile.faculty.name,
        "department": profile.department.name,
        "is_eligible_for_fa": profile.is_eligible_for_fa,
    }


@router.patch("/me/year", dependencies=[Depends(require_role(UserRole.STUDENT))])
def update_year_of_study(
    payload: UpdateYearOfStudy,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not (1 <= payload.year_of_study <= 6):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "year_of_study must be between 1 and 6")

    profile = current_user.student_profile
    profile.year_of_study = payload.year_of_study
    profile.is_eligible_for_fa = check_eligibility(payload.year_of_study, profile.department)
    db.commit()
    return {
        "detail": "Year of study updated",
        "year_of_study": profile.year_of_study,
        "is_eligible_for_fa": profile.is_eligible_for_fa,
    }