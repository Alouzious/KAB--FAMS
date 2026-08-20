"""
Seed script for KAB-FAMS.
Run with: python -m app.seed

Creates:
- Sample Faculties + Departments (with field_attachment_year set)
- One super_admin account (the only account created outside the API)
- One faculty_admin, one department_admin, one supervisor, one student
  — so you can log in at every level and demo the full chain
- Sample TimelineEntry, ContentPage (Guidelines/FAQ), DownloadableForm rows
  so those screens aren't empty either

Safe to re-run: checks for existing records before inserting.
"""

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.services.eligibility_service import check_eligibility

from app.models.academic import Faculty, Department
from app.models.user import User, UserRole
from app.models.admin import AdminProfile
from app.models.supervisor import SupervisorProfile
from app.models.student import StudentProfile
from app.models.timeline import TimelineEntry
from app.models.content_page import ContentPage, PageSlug
from app.models.downloadable_form import DownloadableForm

from datetime import date


def seed():
    # Ensure all tables exist (alembic should normally handle this,
    # but this is a safety net for first-time local setup)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ---------------------------------------------------------
        # 1. FACULTIES + DEPARTMENTS
        # ---------------------------------------------------------
        faculty_data = {
            "Faculty of Computing, Library and Information Science": [
                ("Computer Science", 2),
                ("Information Technology", 2),
                ("Library and Information Science", 2),
            ],
            "Faculty of Business and Management Sciences": [
                ("Business Administration", 3),
                ("Accounting and Finance", 3),
            ],
            "Faculty of Education": [
                ("Education Sciences", 3),
            ],
        }

        faculties = {}
        for faculty_name, departments in faculty_data.items():
            faculty = db.query(Faculty).filter(Faculty.name == faculty_name).first()
            if not faculty:
                faculty = Faculty(name=faculty_name)
                db.add(faculty)
                db.flush()
                print(f"Created faculty: {faculty_name}")
            faculties[faculty_name] = faculty

            for dept_name, fa_year in departments:
                dept = db.query(Department).filter(
                    Department.name == dept_name, Department.faculty_id == faculty.id
                ).first()
                if not dept:
                    dept = Department(
                        name=dept_name,
                        faculty_id=faculty.id,
                        field_attachment_year=fa_year,
                    )
                    db.add(dept)
                    print(f"  Created department: {dept_name} (FA year: {fa_year})")

        db.commit()

        cs_faculty = faculties["Faculty of Computing, Library and Information Science"]
        cs_department = db.query(Department).filter(
            Department.name == "Computer Science", Department.faculty_id == cs_faculty.id
        ).first()

        # ---------------------------------------------------------
        # 2. SUPER ADMIN
        # ---------------------------------------------------------
        super_admin_email = "superadmin@kab.ac.ug"
        super_admin = db.query(User).filter(User.email == super_admin_email).first()
        if not super_admin:
            super_admin = User(
                email=super_admin_email,
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.SUPER_ADMIN,
            )
            db.add(super_admin)
            db.commit()
            print(f"Created super_admin: {super_admin_email} / ChangeMe123!")
        else:
            print("super_admin already exists, skipping")

        # ---------------------------------------------------------
        # 3. SAMPLE FACULTY ADMIN
        # ---------------------------------------------------------
        faculty_admin_email = "facultyadmin.computing@kab.ac.ug"
        fa_user = db.query(User).filter(User.email == faculty_admin_email).first()
        if not fa_user:
            fa_user = User(
                email=faculty_admin_email,
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.FACULTY_ADMIN,
                created_by=super_admin.id,
            )
            db.add(fa_user)
            db.flush()
            db.add(AdminProfile(
                user_id=fa_user.id,
                first_name="Grace",
                last_name="Ahimbisibwe",
                faculty_id=cs_faculty.id,
            ))
            db.commit()
            print(f"Created faculty_admin: {faculty_admin_email} / ChangeMe123!")

        # ---------------------------------------------------------
        # 4. SAMPLE DEPARTMENT ADMIN
        # ---------------------------------------------------------
        dept_admin_email = "deptadmin.cs@kab.ac.ug"
        da_user = db.query(User).filter(User.email == dept_admin_email).first()
        if not da_user:
            da_user = User(
                email=dept_admin_email,
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.DEPARTMENT_ADMIN,
                created_by=fa_user.id,
            )
            db.add(da_user)
            db.flush()
            db.add(AdminProfile(
                user_id=da_user.id,
                first_name="Moses",
                last_name="Golooba",
                department_id=cs_department.id,
            ))
            db.commit()
            print(f"Created department_admin: {dept_admin_email} / ChangeMe123!")

        # ---------------------------------------------------------
        # 5. SAMPLE SUPERVISOR
        # ---------------------------------------------------------
        supervisor_email = "supervisor.cs@kab.ac.ug"
        sup_user = db.query(User).filter(User.email == supervisor_email).first()
        if not sup_user:
            sup_user = User(
                email=supervisor_email,
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.SUPERVISOR,
                created_by=da_user.id,
            )
            db.add(sup_user)
            db.flush()
            db.add(SupervisorProfile(
                user_id=sup_user.id,
                first_name="Innocent",
                last_name="Kawooya",
                phone="+256779345331",
                office="Block A, Level 2, Room 201",
                department_id=cs_department.id,
            ))
            db.commit()
            print(f"Created supervisor: {supervisor_email} / ChangeMe123!")

        # ---------------------------------------------------------
        # 6. SAMPLE STUDENT
        # ---------------------------------------------------------
        student_email = "2023akcs1001gf@kab.ac.ug"
        student_user = db.query(User).filter(User.email == student_email).first()
        if not student_user:
            student_user = User(
                email=student_email,
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.STUDENT,
            )
            db.add(student_user)
            db.flush()

            year_of_study = 3
            is_eligible = check_eligibility(year_of_study, cs_department)

            db.add(StudentProfile(
                user_id=student_user.id,
                first_name="Seanice",
                last_name="Nabasirye",
                registration_number="2023/AKCS/1001/GF",
                admission_year=2023,
                faculty_id=cs_faculty.id,
                department_id=cs_department.id,
                year_of_study=year_of_study,
                is_eligible_for_fa=is_eligible,
            ))
            db.commit()
            print(f"Created student: {student_email} / ChangeMe123! (eligible: {is_eligible})")

        # ---------------------------------------------------------
        # 7. SAMPLE TIMELINE ENTRIES
        # ---------------------------------------------------------
        if db.query(TimelineEntry).count() == 0:
            timeline_entries = [
                ("FA Student Sensitization", date(2026, 1, 1), date(2026, 1, 31)),
                ("Students search for placement", date(2026, 1, 1), date(2026, 5, 9)),
                ("Deadline for uploading placement letter", date(2026, 5, 1), date(2026, 5, 29)),
                ("Assignment of Academic Supervisors to Students", date(2026, 5, 18), date(2026, 5, 22)),
                ("Field Attachment Period", date(2026, 6, 8), date(2026, 8, 1)),
                ("Upload FA Report and Submit Field Supervisor Assessment", date(2026, 8, 1), date(2026, 8, 9)),
            ]
            for activity, start, end in timeline_entries:
                db.add(TimelineEntry(
                    activity=activity, start_date=start, end_date=end, academic_year="2025/2026"
                ))
            db.commit()
            print(f"Created {len(timeline_entries)} timeline entries")

        # ---------------------------------------------------------
        # 8. SAMPLE CONTENT PAGES
        # ---------------------------------------------------------
        if not db.query(ContentPage).filter(ContentPage.slug == PageSlug.GUIDELINES).first():
            db.add(ContentPage(
                slug=PageSlug.GUIDELINES,
                title="Field Attachment Guidelines",
                body="Field attachment is the field-based practical work carried out by "
                     "students for the purpose of gaining hands-on experience. Full "
                     "guidelines to be edited by the super_admin via the CMS endpoint.",
            ))
            print("Created Guidelines content page")

        if not db.query(ContentPage).filter(ContentPage.slug == PageSlug.FAQ).first():
            db.add(ContentPage(
                slug=PageSlug.FAQ,
                title="Frequently Asked Questions",
                body="Q: What if I can't find a placement?\nA: Contact your departmental "
                     "coordinator for assistance. (Edit this via the CMS endpoint.)",
            ))
            print("Created FAQ content page")

        db.commit()

        print("\nSeeding complete.")
        print("=" * 50)
        print("Login credentials (all passwords: ChangeMe123!)")
        print(f"  super_admin:       {super_admin_email}")
        print(f"  faculty_admin:     {faculty_admin_email}")
        print(f"  department_admin:  {dept_admin_email}")
        print(f"  supervisor:        {supervisor_email}")
        print(f"  student:           {student_email}")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    seed()