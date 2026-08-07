from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class GeneratePosterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: UUID
    event_type: Literal["birthday", "work_anniversary"]
    event_date: date
    occurrence_date: date
    person_id: UUID
    person_name: str
    photo_path: str
    template_key: str

    @field_validator("person_name", "photo_path", "template_key")
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def template_matches_event(self):
        supported = {
            "birthday": {"birthday-default"},
            "work_anniversary": {
                "anniversary-default",
                "work-anniversary",
            },
        }[self.event_type]
        if self.template_key not in supported:
            raise ValueError(
                f"{self.event_type} requires one of these template keys: "
                f"{', '.join(sorted(supported))}"
            )
        return self


class ScheduleRequest(BaseModel):
    run_date: date | None = None
