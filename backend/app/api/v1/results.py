from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_role, get_current_user
from app.models.user import User, UserRole
from app.models.result import Result, ResultStatus
from app.models.supervisor import SupervisorAssignment, SupervisorProfile
from app.services.result_service import compute_final_score
from app.schemas.public import ResultOut, ResultScoreEntry

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/me", response_model=ResultOut, dependencies=[Depends(require_role(UserRole.STUDENT))])
def get_my_result(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = db.query(Result).filter(Result.student_id == current_user.student_profile.id).first()
    if not result or result.status != ResultStatus.RELEASED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Results not yet released")
    return result


@router.post("/score", dependencies=[Depends(require_role(UserRole.SUPERVISOR))])
def enter_score(
    payload: ResultScoreEntry,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supervisor = db.query(SupervisorProfile).filter(SupervisorProfile.user_id == current_user.id).first()
    assignment = db.query(SupervisorAssignment).filter(
        SupervisorAssignment.supervisor_id == supervisor.id,
        SupervisorAssignment.student_id == payload.student_id,
    ).first()
    if not assignment:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This student is not assigned to you")

    result = db.query(Result).filter(Result.student_id == payload.student_id).first()
    if not result:
        result = Result(student_id=payload.student_id, graded_by=current_user.id)
        db.add(result)

    if payload.field_supervisor_score is not None:
        result.field_supervisor_score = payload.field_supervisor_score
    if payload.academic_supervisor_score is not None:
        result.academic_supervisor_score = payload.academic_supervisor_score

    result = compute_final_score(result)
    db.commit()
    db.refresh(result)
    return {
        "detail": "Score recorded",
        "final_score": result.final_score,
        "grade_letter": result.grade_letter,
        "status": result.status.value,
    }


@router.post(
    "/{student_id}/release",
    dependencies=[Depends(require_role(UserRole.DEPARTMENT_ADMIN))],
)
def release_result(student_id: str, db: Session = Depends(get_db)):
    result = db.query(Result).filter(Result.student_id == student_id).first()
    if not result or result.status != ResultStatus.SUBMITTED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Result is not ready to be released")
    result.status = ResultStatus.RELEASED
    db.commit()
    return {"detail": "Result released to student"}