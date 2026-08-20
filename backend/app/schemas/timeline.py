from datetime import date
from pydantic import BaseModel, computed_field


class TimelineEntryOut(BaseModel):
    id: str
    activity: str
    start_date: date
    end_date: date
    academic_year: str

    class Config:
        from_attributes = True

    @computed_field
    @property
    def remark(self) -> str:
        today = date.today()
        if today > self.end_date:
            return "Overdue"
        elif today < self.start_date:
            return "Upcoming"
        return "On Schedule"