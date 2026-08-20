from app.models.student import StudentProfile


def generate_placement_letter_context(student: StudentProfile) -> dict:
    """
    Builds the data dict injected into the placement request letter PDF.
    Used by GET /api/v1/placements/request-letter.
    """
    return {
        "student_name": f"{student.first_name} {student.last_name}",
        "registration_number": getattr(student, "registration_number", "N/A"),
        "department": student.department.name,
        "faculty": student.faculty.name,
        "year_of_study": student.year_of_study,
    }