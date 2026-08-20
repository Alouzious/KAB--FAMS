from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    auth, students, supervisors, admin, placements,
    attendance, reports, public, organisations, results,
)

app = FastAPI(
    title="KAB-FAMS API",
    description="Kabale University Field Attachment Management System "
                 "handles student placement, attendance tracking, weekly "
                 "progress reporting, and supervisor coordination across "
                 "faculties and departments.",
    version="1.0.0",
    contact={"name": "Beta-Tech Labs Co. Limited", "email": "alouzious@gmail.com"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Registration and login for students, supervisors, and admins."},
        {"name": "students", "description": "Student profile and dashboard endpoints."},
        {"name": "supervisors", "description": "Field and academic supervisor endpoints."},
        {"name": "admin", "description": "Admin-only management endpoints."},
        {"name": "placements", "description": "Placement details and request letter generation."},
        {"name": "attendance", "description": "Clock-in/clock-out and attendance history."},
        {"name": "reports", "description": "Weekly progress reports and final report submission."},
        {"name": "public", "description": "Timeline, guidelines, FAQ, downloads, and feedback."},
        {"name": "organisations", "description": "Partner organisations and internship opportunities."},
        {"name": "results", "description": "Field attachment results and scoring."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(supervisors.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(placements.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(public.router, prefix="/api/v1")
app.include_router(organisations.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")


@app.get("/", tags=["health"])
def health_check():
    return {"status": "KAB-FAMS API is running"}