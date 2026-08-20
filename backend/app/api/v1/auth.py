from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.eligibility_service import check_eligibility

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    extract_admission_year,
)
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.academic import Department
from app.schemas.auth import StudentRegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/student", response_model=TokenResponse)
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    department = db.query(Department).filter(Department.id == payload.department_id).first()
    if not department:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid department")

    # Eligibility is computed from department rules, not hardcoded
    is_eligible = check_eligibility(payload.year_of_study, department)

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    profile = StudentProfile(
        user_id=user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        admission_year=extract_admission_year(payload.email),
        faculty_id=payload.faculty_id,
        department_id=payload.department_id,
        year_of_study=payload.year_of_study,
        is_eligible_for_fa=is_eligible,
    )
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, is_eligible_for_fa=is_eligible)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    is_eligible = None
    if user.student_profile:
        is_eligible = user.student_profile.is_eligible_for_fa

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, is_eligible_for_fa=is_eligible)