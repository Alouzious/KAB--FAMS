from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.deps import get_current_user, require_eligible_student, require_role
from app.models.user import User, UserRole
from app.models.progress_report import ProgressReport
from app.models.final_report import FinalReport, ReportStatus
from app.schemas.report import (
    ProgressReportCreate, ProgressReportOut, ProgressReportComment,
    FinalReportSubmit, FinalReportOut, FinalReportReview,
)

router = APIRouter(prefix="/reports", tags=["reports"])


# ---- Progress reports ----

@router.post("/progress", response_model=ProgressReportOut, dependencies=[Depends(require_eligible_student)])
def submit_progress_report(
    payload: ProgressReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = ProgressReport(student_id=current_user.student_profile.id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/progress/me", response_model=list[ProgressReportOut], dependencies=[Depends(require_role(UserRole.STUDENT))])
def my_progress_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(ProgressReport)
        .filter(ProgressReport.student_id == current_user.student_profile.id)
        .order_by(ProgressReport.week_ending.desc())
        .all()
    )


@router.get(
    "/progress/student/{student_id}",
    response_model=list[ProgressReportOut],
    dependencies=[Depends(require_role(UserRole.SUPERVISOR))],
)
def student_progress_reports(student_id: str, db: Session = Depends(get_db)):
    return (
        db.query(ProgressReport)
        .filter(ProgressReport.student_id == student_id)
        .order_by(ProgressReport.week_ending.desc())
        .all()
    )


@router.patch(
    "/progress/{report_id}/comment",
    response_model=ProgressReportOut,
    dependencies=[Depends(require_role(UserRole.SUPERVISOR))],
)
def comment_progress_report(report_id: str, payload: ProgressReportComment, db: Session = Depends(get_db)):
    report = db.query(ProgressReport).filter(ProgressReport.id == report_id).first()
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Progress report not found")
    report.supervisor_comments = payload.supervisor_comments
    db.commit()
    db.refresh(report)
    return report


# ---- Final report ----
# NOTE: assumes file already uploaded to Cloudinary via cloudinary_service,
# and file_url/file_public_id passed in here. Show me cloudinary_service.py
# if you want this wired to accept the raw file upload directly.

@router.post("/final", response_model=FinalReportOut, dependencies=[Depends(require_eligible_student)])
def submit_final_report(
    payload: FinalReportSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(FinalReport).filter(FinalReport.student_id == current_user.student_profile.id).first()
    if existing:
        existing.file_url = payload.file_url
        existing.file_public_id = payload.file_public_id
        existing.status = ReportStatus.SUBMITTED
        existing.reviewed_at = None
        db.commit()
        db.refresh(existing)
        return existing

    report = FinalReport(student_id=current_user.student_profile.id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/final/me", response_model=FinalReportOut, dependencies=[Depends(require_role(UserRole.STUDENT))])
def my_final_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(FinalReport).filter(FinalReport.student_id == current_user.student_profile.id).first()
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No final report submitted yet")
    return report


@router.patch(
    "/final/{report_id}/review",
    response_model=FinalReportOut,
    dependencies=[Depends(require_role(UserRole.SUPERVISOR))],
)
def review_final_report(report_id: str, payload: FinalReportReview, db: Session = Depends(get_db)):
    report = db.query(FinalReport).filter(FinalReport.id == report_id).first()
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Final report not found")
    report.status = payload.status
    report.reviewer_notes = payload.reviewer_notes
    report.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)
    return report
