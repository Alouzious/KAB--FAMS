from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.api.deps import require_role, get_current_user
from app.models.user import User, UserRole
from app.models.timeline import TimelineEntry
from app.models.content_page import ContentPage, PageSlug
from app.models.feedback import Feedback
from app.models.downloadable_form import DownloadableForm
from app.schemas.public import (
    TimelineEntryOut, ContentPageOut, ContentPageUpdate,
    FeedbackCreate, DownloadableFormOut,
)

router = APIRouter(tags=["public"])


def _compute_remark(entry: TimelineEntry) -> str:
    today = date.today()
    if today > entry.end_date:
        return "Overdue"
    elif today < entry.start_date:
        return "Upcoming"
    return "On Schedule"


# ---------- TIMELINE (public — any logged-in user can view) ----------
@router.get("/timeline", response_model=list[TimelineEntryOut])
def list_timeline(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entries = db.query(TimelineEntry).order_by(TimelineEntry.start_date).all()
    return [
        TimelineEntryOut(
            id=str(e.id), activity=e.activity, start_date=e.start_date,
            end_date=e.end_date, academic_year=e.academic_year, remark=_compute_remark(e),
        )
        for e in entries
    ]


# ---------- GUIDELINES / FAQ (public read, super_admin edit) ----------
@router.get("/guidelines", response_model=ContentPageOut)
def get_guidelines(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = db.query(ContentPage).filter(ContentPage.slug == PageSlug.GUIDELINES).first()
    if not page:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guidelines not yet published")
    return ContentPageOut(slug=page.slug.value, title=page.title, body=page.body)


@router.put("/guidelines", response_model=ContentPageOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
def update_guidelines(payload: ContentPageUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = db.query(ContentPage).filter(ContentPage.slug == PageSlug.GUIDELINES).first()
    if not page:
        page = ContentPage(slug=PageSlug.GUIDELINES, title=payload.title, body=payload.body)
        db.add(page)
    else:
        page.title = payload.title
        page.body = payload.body
    page.updated_by = current_user.id
    db.commit()
    db.refresh(page)
    return ContentPageOut(slug=page.slug.value, title=page.title, body=page.body)


@router.get("/faq", response_model=ContentPageOut)
def get_faq(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = db.query(ContentPage).filter(ContentPage.slug == PageSlug.FAQ).first()
    if not page:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "FAQ not yet published")
    return ContentPageOut(slug=page.slug.value, title=page.title, body=page.body)


@router.put("/faq", response_model=ContentPageOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
def update_faq(payload: ContentPageUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = db.query(ContentPage).filter(ContentPage.slug == PageSlug.FAQ).first()
    if not page:
        page = ContentPage(slug=PageSlug.FAQ, title=payload.title, body=payload.body)
        db.add(page)
    else:
        page.title = payload.title
        page.body = payload.body
    page.updated_by = current_user.id
    db.commit()
    db.refresh(page)
    return ContentPageOut(slug=page.slug.value, title=page.title, body=page.body)


# ---------- DOWNLOADS (public read) ----------
@router.get("/downloads", response_model=list[DownloadableFormOut])
def list_downloads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    forms = db.query(DownloadableForm).all()
    return forms


# ---------- FEEDBACK (student submits) ----------
@router.post("/feedback", dependencies=[Depends(require_role(UserRole.STUDENT))])
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feedback = Feedback(
        student_id=current_user.student_profile.id,
        process_feedback=payload.process_feedback,
        system_feedback=payload.system_feedback,
    )
    db.add(feedback)
    db.commit()
    return {"detail": "Thank you for your feedback"}