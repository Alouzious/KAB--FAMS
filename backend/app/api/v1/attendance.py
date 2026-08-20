from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_eligible_student, require_role
from app.models.user import User, UserRole
from app.models.attendance import AttendanceLog
from app.schemas.attendance import ClockRequest, AttendanceLogOut

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/clock", response_model=AttendanceLogOut, dependencies=[Depends(require_eligible_student)])
def clock(
    payload: ClockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = AttendanceLog(
        student_id=current_user.student_profile.id,
        **payload.model_dump(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/me", response_model=list[AttendanceLogOut], dependencies=[Depends(require_role(UserRole.STUDENT))])
def my_attendance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(AttendanceLog)
        .filter(AttendanceLog.student_id == current_user.student_profile.id)
        .order_by(AttendanceLog.timestamp.desc())
        .all()
    )


@router.get(
    "/student/{student_id}",
    response_model=list[AttendanceLogOut],
    dependencies=[Depends(require_role(UserRole.SUPERVISOR, UserRole.DEPARTMENT_ADMIN, UserRole.FACULTY_ADMIN))],
)
def student_attendance(student_id: str, db: Session = Depends(get_db)):
    return (
        db.query(AttendanceLog)
        .filter(AttendanceLog.student_id == student_id)
        .order_by(AttendanceLog.timestamp.desc())
        .all()
    )
