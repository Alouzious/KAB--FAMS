from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID


class TimelineEntryOut(BaseModel):
    id: str
    activity: str
    start_date: date
    end_date: date
    academic_year: str
    remark: str  # computed — On Schedule / Upcoming / Overdue

    class Config:
        from_attributes = True


class ContentPageOut(BaseModel):
    slug: str
    title: str
    body: str

    class Config:
        from_attributes = True


class ContentPageUpdate(BaseModel):
    title: str
    body: str


class FeedbackCreate(BaseModel):
    process_feedback: str | None = None
    system_feedback: str | None = None


class DownloadableFormOut(BaseModel):
    id: str
    name: str
    file_url: str

    class Config:
        from_attributes = True


class InternshipOpportunityOut(BaseModel):
    id: str
    organisation_name: str
    district: str | None
    intern_attributes: str | None
    incentive_type: str
    num_slots: int
    contact_person: str | None
    contact_email: str | None
    contact_phone: str | None
    date_posted: date

    class Config:
        from_attributes = True


class InternshipOpportunityCreate(BaseModel):
    organisation_name: str
    district: str | None = None
    intern_attributes: str | None = None
    incentive_type: str = "intern_given_no_incentive"
    num_slots: int = 1
    contact_person: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None


class OrganisationOut(BaseModel):
    id: str
    name: str
    district: str | None
    address: str | None
    email: str | None
    phone: str | None
    rating_average: float | None
    rating_count: int

    class Config:
        from_attributes = True


class OrganisationRatingCreate(BaseModel):
    organisation_id: UUID
    score: int  # 1-5
    comment: str | None = None


class ResultOut(BaseModel):
    field_supervisor_score: float | None
    academic_supervisor_score: float | None
    final_score: float | None
    grade_letter: str | None
    status: str

    class Config:
        from_attributes = True


class ResultScoreEntry(BaseModel):
    student_id: UUID
    field_supervisor_score: float | None = None
    academic_supervisor_score: float | None = None


class UpdateYearOfStudy(BaseModel):
    year_of_study: int


class TeamMemberOut(BaseModel):
    role_label: str
    name: str
    email: str | None
    phone: str | None
    office: str | None = None


class SupervisoryTeamOut(BaseModel):
    field_supervisor: TeamMemberOut | None
    academic_supervisor: TeamMemberOut | None
    department_coordinator: TeamMemberOut | None
    dean: TeamMemberOut | None