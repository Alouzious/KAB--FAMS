from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.api.deps import require_role, get_faculty_scope, get_department_scope
from app.models.user import User, UserRole
from app.models.admin import AdminProfile
from app.models.supervisor import SupervisorProfile, SupervisorAssignment
from app.models.student import StudentProfile
from app.models.academic import Faculty, Department
from app.schemas.admin import (
    CreateFacultyRequest,
    CreateFacultyAdminRequest,
    CreateDepartmentRequest,
    CreateDepartmentAdminRequest,
    CreateSupervisorRequest,
    AssignSupervisorRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# =========================================================
# SUPER ADMIN — whole system
# =========================================================

@router.post("/faculties", dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
def create_faculty(payload: CreateFacultyRequest, db: Session = Depends(get_db)):
    if db.query(Faculty).filter(Faculty.name == payload.name).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Faculty already exists")
    faculty = Faculty(name=payload.name)
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return {"id": str(faculty.id), "name": faculty.name}


@router.post("/faculty-admins", dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
def create_faculty_admin(payload: CreateFacultyAdminRequest, db: Session = Depends(get_db)):
    if not db.query(Faculty).filter(Faculty.id == payload.faculty_id).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid faculty")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.FACULTY_ADMIN)
    db.add(user)
    db.flush()

    db.add(AdminProfile(
        user_id=user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        faculty_id=payload.faculty_id,
    ))
    db.commit()
    return {"detail": f"Faculty admin created for faculty {payload.faculty_id}"}


# =========================================================
# FACULTY ADMIN — scoped to own faculty
# =========================================================

@router.post("/departments", dependencies=[Depends(require_role(UserRole.FACULTY_ADMIN))])
def create_department(
    payload: CreateDepartmentRequest,
    db: Session = Depends(get_db),
    faculty_id: str = Depends(get_faculty_scope),
):
    department = Department(
        name=payload.name,
        faculty_id=faculty_id,
        field_attachment_year=payload.field_attachment_year,
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return {"id": str(department.id), "name": department.name, "faculty_id": faculty_id}


@router.post("/department-admins", dependencies=[Depends(require_role(UserRole.FACULTY_ADMIN))])
def create_department_admin(
    payload: CreateDepartmentAdminRequest,
    db: Session = Depends(get_db),
    faculty_id: str = Depends(get_faculty_scope),
):
    department = db.query(Department).filter(Department.id == payload.department_id).first()
    if not department:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid department")
    if str(department.faculty_id) != faculty_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This department is not in your faculty")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.DEPARTMENT_ADMIN)
    db.add(user)
    db.flush()

    db.add(AdminProfile(
        user_id=user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        department_id=payload.department_id,
    ))
    db.commit()
    return {"detail": f"Department admin created for department {payload.department_id}"}


# =========================================================
# SUPERVISOR CREATION — allowed for BOTH faculty_admin and department_admin
# =========================================================

@router.post("/supervisors", dependencies=[Depends(require_role(UserRole.FACULTY_ADMIN, UserRole.DEPARTMENT_ADMIN))])
def create_supervisor(
    payload: CreateSupervisorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FACULTY_ADMIN, UserRole.DEPARTMENT_ADMIN)),
):
    # Resolve which department this supervisor belongs to, based on who's creating them
    if current_user.role == UserRole.DEPARTMENT_ADMIN:
        department_id = current_user.admin_profile.department_id
    else:  # FACULTY_ADMIN — must specify department_id, and it must be in their faculty
        if not payload.department_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "department_id is required when creating a supervisor as a faculty admin")
        department = db.query(Department).filter(Department.id == payload.department_id).first()
        if not department:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid department")
        if str(department.faculty_id) != str(current_user.admin_profile.faculty_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This department is not in your faculty")
        department_id = payload.department_id

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.SUPERVISOR)
    db.add(user)
    db.flush()

    db.add(SupervisorProfile(
        user_id=user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        office=payload.office,
        department_id=department_id,
    ))
    db.commit()
    return {"detail": "Supervisor created successfully", "department_id": str(department_id)}


# =========================================================
# DEPARTMENT ADMIN — assign supervisor to student, list own students
# =========================================================

@router.post("/assign-supervisor", dependencies=[Depends(require_role(UserRole.DEPARTMENT_ADMIN))])
def assign_supervisor(
    payload: AssignSupervisorRequest,
    db: Session = Depends(get_db),
    department_id: str = Depends(get_department_scope),
):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    supervisor = db.query(SupervisorProfile).filter(SupervisorProfile.id == payload.supervisor_id).first()

    if not student or not supervisor:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid student or supervisor")
    if str(student.department_id) != department_id or str(supervisor.department_id) != department_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Student or supervisor is outside your department")

    existing = db.query(SupervisorAssignment).filter(SupervisorAssignment.student_id == student.id).first()
    if existing:
        existing.supervisor_id = supervisor.id
    else:
        db.add(SupervisorAssignment(student_id=student.id, supervisor_id=supervisor.id))

    db.commit()
    return {"detail": "Supervisor assigned successfully"}


@router.get("/students", dependencies=[Depends(require_role(UserRole.DEPARTMENT_ADMIN))])
def list_department_students(db: Session = Depends(get_db), department_id: str = Depends(get_department_scope)):
    students = db.query(StudentProfile).filter(StudentProfile.department_id == department_id).all()
    return [
        {"id": str(s.id), "name": f"{s.first_name} {s.last_name}", "year_of_study": s.year_of_study, "is_eligible_for_fa": s.is_eligible_for_fa}
        for s in students
    ]


@router.get("/supervisors", dependencies=[Depends(require_role(UserRole.DEPARTMENT_ADMIN, UserRole.FACULTY_ADMIN))])
def list_supervisors(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DEPARTMENT_ADMIN, UserRole.FACULTY_ADMIN)),
):
    if current_user.role == UserRole.DEPARTMENT_ADMIN:
        supervisors = db.query(SupervisorProfile).filter(
            SupervisorProfile.department_id == current_user.admin_profile.department_id
        ).all()
    else:
        dept_ids = [d.id for d in db.query(Department).filter(Department.faculty_id == current_user.admin_profile.faculty_id).all()]
        supervisors = db.query(SupervisorProfile).filter(SupervisorProfile.department_id.in_(dept_ids)).all()

    return [
        {"id": str(s.id), "name": f"{s.first_name} {s.last_name}", "department_id": str(s.department_id)}
        for s in supervisors
    ]