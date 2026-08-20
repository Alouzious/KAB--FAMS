from app.models.academic import Department


def check_eligibility(year_of_study: int, department: Department) -> bool:
    """
    Single source of truth for field attachment eligibility.
    Used at registration AND whenever a student's year_of_study is updated.
    """
    return year_of_study >= department.field_attachment_year