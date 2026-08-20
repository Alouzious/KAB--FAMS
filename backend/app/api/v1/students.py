from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import Faculty, Department
from app.models.supervisor import FieldSupervisor, SupervisorAssignment
from app.models.admin import AdminProfile
from app.services.eligibility_service import check_eligibility
from app.schemas.common import FacultyOut, DepartmentOut
from app.schemas.public import UpdateYearOfStudy, SupervisoryTeamOut, TeamMemberOut

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


@router.get("/me/supervisory-team", response_model=SupervisoryTeamOut)
def my_supervisory_team(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = current_user.student_profile

    fs = db.query(FieldSupervisor).filter(FieldSupervisor.student_id == profile.id).first()
    field_supervisor = TeamMemberOut(
        role_label="Field Supervisor",
        name=f"{fs.last_name}, {fs.first_name}",
        email=fs.email,
        phone=fs.phone,
    ) if fs else None

    assignment = db.query(SupervisorAssignment).filter(SupervisorAssignment.student_id == profile.id).first()
    academic_supervisor = None
    if assignment:
        sup = assignment.supervisor
        academic_supervisor = TeamMemberOut(
            role_label="Academic Supervisor",
            name=f"{sup.first_name} {sup.last_name}",
            email=sup.user.email,
            phone=sup.phone,
            office=sup.office,
        )

    dept_admin = db.query(AdminProfile).join(User).filter(
        AdminProfile.department_id == profile.department_id,
        User.role == UserRole.DEPARTMENT_ADMIN,
    ).first()
    department_coordinator = TeamMemberOut(
        role_label="Departmental Coordinator",
        name=f"{dept_admin.first_name} {dept_admin.last_name}",
        email=dept_admin.user.email,
        phone=dept_admin.phone,
    ) if dept_admin else None

    faculty_admin = db.query(AdminProfile).join(User).filter(
        AdminProfile.faculty_id == profile.faculty_id,
        User.role == UserRole.FACULTY_ADMIN,
    ).first()
    dean = TeamMemberOut(
        role_label="Dean",
        name=f"{faculty_admin.first_name} {faculty_admin.last_name}",
        email=faculty_admin.user.email,
        phone=faculty_admin.phone,
    ) if faculty_admin else None

    return SupervisoryTeamOut(
        field_supervisor=field_supervisor,
        academic_supervisor=academic_supervisor,
        department_coordinator=department_coordinator,
        dean=dean,
    )