from typing import List, Optional, Set
from pydantic import (
    BaseModel,
    Field,
    StrictStr,
    StrictBool,
    ValidationError,
    field_validator,
    model_validator,
    ConfigDict
)


class Proof(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: StrictStr
    url: StrictStr

class Constraints(BaseModel):
    model_config = ConfigDict(extra='forbid')
    max_apps_per_day: int
    min_match_score: float
    blocked_companies: List[StrictStr] = []

class Bullet(BaseModel):
    model_config = ConfigDict(extra='forbid')
    description: StrictStr
    skills: List[StrictStr]
    verified: StrictBool
    proofs: Optional[List[Proof]] = None

    @model_validator(mode='after')
    def check_verified(self):
        if not self.verified:
            raise ValueError('Every bullet must have verified == true')
        return self

class Project(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: StrictStr
    description: StrictStr
    skills: List[StrictStr]
    bullets: List[Bullet]

class Education(BaseModel):
    model_config = ConfigDict(extra='forbid')
    institution: StrictStr
    degree: Optional[StrictStr] = None
    field_of_study: Optional[StrictStr] = None

class StudentArtifactPack(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source_resume_hash: StrictStr = Field(..., description="SHA256 hash of the source resume")
    skill_vocab: List[StrictStr] = Field(..., description="Vocabulary of all legal skills")
    education: List[Education]
    projects: List[Project]
    constraints: Optional[Constraints] = None

    @field_validator('skill_vocab')
    @classmethod
    def check_skill_vocab_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("skill_vocab must contain only unique skills")
        return v

    @model_validator(mode='after')
    def validate_all_skills_and_bullets(self):
        skill_vocab: Set[str] = set(self.skill_vocab)

        # Validate project skills
        for project in self.projects:
            for ps in project.skills:
                if ps not in skill_vocab:
                    raise ValueError(
                        f"Project skill '{ps}' in project '{project.name}' is not in skill_vocab"
                    )
            for bullet in project.bullets:
                # This triggers Bullet validation (verified == True) on construction
                for bs in bullet.skills:
                    if bs not in skill_vocab:
                        raise ValueError(
                            f"Bullet skill '{bs}' in project '{project.name}' is not in skill_vocab"
                        )
        return self