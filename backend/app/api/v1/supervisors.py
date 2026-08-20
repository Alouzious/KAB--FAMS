from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_role
from app.models.user import User, UserRole
from app.models.supervisor import SupervisorAssignment, SupervisorProfile
from app.models.student import StudentProfile
from app.models.progress_report import ProgressReport
from app.models.attendance import AttendanceLog

router = APIRouter(prefix="/supervisors", tags=["supervisors"])


def _get_supervisor_profile(db: Session, current_user: User) -> SupervisorProfile:
    profile = db.query(SupervisorProfile).filter(SupervisorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Supervisor profile not found")
    return profile


@router.get("/me")
def my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPERVISOR)),
):
    profile = _get_supervisor_profile(db, current_user)
    return {
        "name": f"{profile.first_name} {profile.last_name}",
        "email": current_user.email,
        "department": profile.department.name,
        "office": profile.office,
        "phone": profile.phone,
    }


@router.get("/me/students")
def my_assigned_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPERVISOR)),
):
    """This is the core supervisor dashboard view — only students assigned to them."""
    profile = _get_supervisor_profile(db, current_user)
    assignments = db.query(SupervisorAssignment).filter(SupervisorAssignment.supervisor_id == profile.id).all()

    result = []
    for a in assignments:
        student = a.student
        result.append({
            "student_id": str(student.id),
            "name": f"{student.first_name} {student.last_name}",
            "year_of_study": student.year_of_study,
            "department": student.department.name,
        })
    return result


@router.get("/me/students/{student_id}/reports")
def student_reports(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPERVISOR)),
):
    """Guard: supervisor can only view reports for students actually assigned to them."""
    profile = _get_supervisor_profile(db, current_user)
    assignment = db.query(SupervisorAssignment).filter(
        SupervisorAssignment.supervisor_id == profile.id,
        SupervisorAssignment.student_id == student_id,
    ).first()
    if not assignment:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This student is not assigned to you")

    reports = db.query(ProgressReport).filter(ProgressReport.student_id == student_id).order_by(ProgressReport.week_ending).all()
    return [
        {
            "week_ending": str(r.week_ending),
            "tasks_completed": r.tasks_completed,
            "tasks_in_progress": r.tasks_in_progress,
            "problems_challenges": r.problems_challenges,
            "supervisor_comments": r.supervisor_comments,
        }
        for r in reports
    ]


@router.get("/me/students/{student_id}/attendance")
def student_attendance(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPERVISOR)),
):
    profile = _get_supervisor_profile(db, current_user)
    assignment = db.query(SupervisorAssignment).filter(
        SupervisorAssignment.supervisor_id == profile.id,
        SupervisorAssignment.student_id == student_id,
    ).first()
    if not assignment:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This student is not assigned to you")

    logs = db.query(AttendanceLog).filter(AttendanceLog.student_id == student_id).order_by(AttendanceLog.timestamp.desc()).all()
    return [
        {
            "clock_type": log.clock_type.value,
            "timestamp": str(log.timestamp),
            "approximate_location": log.approximate_location,
            "accuracy_meters": log.accuracy_meters,
        }
        for log in logs
    ]