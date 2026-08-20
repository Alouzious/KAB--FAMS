from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.database import get_db
from app.api.deps import get_current_user, require_eligible_student, require_role
from app.models.user import User, UserRole
from app.models.placement import Placement
from app.models.supervisor import FieldSupervisor
from app.schemas.placement import (
    PlacementOut, FieldSupervisorCreate, FieldSupervisorOut,
)
from app.services.cloudinary_service import upload_file
from app.services.letter_generator import generate_placement_letter_context

router = APIRouter(prefix="/placements", tags=["placements"])


# ---------- PLACEMENT (with file upload) ----------

@router.post("/", response_model=PlacementOut, dependencies=[Depends(require_eligible_student)])
def create_placement(
    organisation_name: str = Form(...),
    organisation_email: str | None = Form(None),
    district: str | None = Form(None),
    address: str | None = Form(None),
    letter: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploaded = upload_file(letter.file, folder="placement-letters")

    existing = db.query(Placement).filter(Placement.student_id == current_user.student_profile.id).first()
    if existing:
        existing.organisation_name = organisation_name
        existing.organisation_email = organisation_email
        existing.district = district
        existing.address = address
        existing.placement_letter_url = uploaded["url"]
        db.commit()
        db.refresh(existing)
        return existing

    placement = Placement(
        student_id=current_user.student_profile.id,
        organisation_name=organisation_name,
        organisation_email=organisation_email,
        district=district,
        address=address,
        placement_letter_url=uploaded["url"],
    )
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


# ---------- FIELD SUPERVISOR DETAILS ----------

@router.post("/field-supervisor", response_model=FieldSupervisorOut, dependencies=[Depends(require_eligible_student)])
def upsert_field_supervisor(
    payload: FieldSupervisorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(FieldSupervisor).filter(FieldSupervisor.student_id == current_user.student_profile.id).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing

    fs = FieldSupervisor(student_id=current_user.student_profile.id, **payload.model_dump())
    db.add(fs)
    db.commit()
    db.refresh(fs)
    return fs


@router.get("/field-supervisor/me", response_model=FieldSupervisorOut, dependencies=[Depends(require_role(UserRole.STUDENT))])
def my_field_supervisor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fs = db.query(FieldSupervisor).filter(FieldSupervisor.student_id == current_user.student_profile.id).first()
    if not fs:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No field supervisor recorded yet")
    return fs


# ---------- PLACEMENT REQUEST LETTER (PDF) ----------

@router.get("/request-letter", dependencies=[Depends(require_role(UserRole.STUDENT))])
def download_request_letter(current_user: User = Depends(get_current_user)):
    ctx = generate_placement_letter_context(current_user.student_profile)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "KABALE UNIVERSITY")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 90, "P.O. Box 317, Kabale, Uganda")
    c.line(72, height - 100, width - 72, height - 100)

    c.setFont("Helvetica", 11)
    c.drawString(72, height - 140, "Date: ____________________")
    c.drawString(72, height - 180, "TO WHOM IT MAY CONCERN")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, height - 210, "RE: REQUEST FOR FIELD ATTACHMENT PLACEMENT")

    c.setFont("Helvetica", 11)
    text = c.beginText(72, height - 240)
    text.setLeading(18)
    text.textLines([
        f"This is to introduce {ctx['student_name']}, Registration Number:",
        f"{ctx['registration_number']}, a student of {ctx['department']},",
        f"{ctx['faculty']}, currently in Year {ctx['year_of_study']} at Kabale University.",
        "",
        "The above named is required to undertake a field attachment placement",
        "as part of the requirements for their degree programme. We kindly",
        "request your organisation to consider hosting the student for this",
        "period.",
        "",
        "Any assistance accorded to the student will be highly appreciated.",
        "",
        "Yours faithfully,",
        "",
        "FA Coordination Team",
        "Kabale University",
    ])
    c.drawText(text)
    c.save()
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=placement_request_letter.pdf"},
    )