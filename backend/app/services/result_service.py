from app.models.result import Result, ResultStatus

# Adjust these weights to match your department's actual grading policy
FIELD_SUPERVISOR_WEIGHT = 0.6
ACADEMIC_SUPERVISOR_WEIGHT = 0.4


def compute_final_score(result: Result) -> Result:
    if result.field_supervisor_score is None or result.academic_supervisor_score is None:
        return result  # not ready yet — both scores required

    final = (
        result.field_supervisor_score * FIELD_SUPERVISOR_WEIGHT
        + result.academic_supervisor_score * ACADEMIC_SUPERVISOR_WEIGHT
    )
    result.final_score = round(final, 2)
    result.grade_letter = _score_to_grade(final)
    result.status = ResultStatus.SUBMITTED
    return result


def _score_to_grade(score: float) -> str:
    if score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "F"