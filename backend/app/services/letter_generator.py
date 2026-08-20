from app.models.student import StudentProfile


def generate_placement_letter_context(student: StudentProfile) -> dict:
    """
    Builds the data dict that will be injected into a PDF template
    (using a library like WeasyPrint or reportlab — wire that up when
    we get to this endpoint specifically).
    """
    return {
        "student_name": f"{student.first_name} {student.last_name}",
        "registration_number": student.registration_number,
        "department": student.department.name,
        "faculty": student.faculty.name,
        "year_of_study": student.year_of_study,
    }