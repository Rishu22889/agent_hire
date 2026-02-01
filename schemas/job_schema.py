from typing import List
from pydantic import BaseModel, Field, StrictStr, StrictInt, field_validator, ConfigDict

class JobListing(BaseModel):
    model_config = ConfigDict(extra='forbid')
    job_id: StrictStr
    company: StrictStr
    role: StrictStr
    location: StrictStr
    required_skills: List[StrictStr]
    min_experience_years: StrictInt

    @field_validator("min_experience_years")
    @classmethod
    def min_experience_years_non_negative(cls, v):
        if v < 0:
            raise ValueError("min_experience_years must be >= 0")
        return v