"""
User Profile Schema - SINGLE SOURCE OF TRUTH
This is the authoritative schema for persistent user profiles.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class BasicInfo(BaseModel):
    """Basic personal information."""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location/address")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v


class Education(BaseModel):
    """Education entry in user profile."""
    institution: str = Field(..., description="Educational institution name")
    degree: Optional[str] = Field(None, description="Degree type (e.g., Bachelor's, Master's)")
    field: Optional[str] = Field(None, description="Field of study")
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End year (or expected)")
    
    @validator('start_year', 'end_year')
    def validate_years(cls, v):
        if v is not None and (v < 1900 or v > 2030):
            raise ValueError('Year must be between 1900 and 2030')
        return v
    
    @validator('end_year')
    def validate_end_after_start(cls, v, values):
        if v is not None and 'start_year' in values and values['start_year'] is not None:
            if v < values['start_year']:
                raise ValueError('End year must be after start year')
        return v


class Certificate(BaseModel):
    """Certificate entry in user profile."""
    name: str = Field(..., description="Certificate name")
    issuer: str = Field(..., description="Issuing organization")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM format)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM format)")
    credential_id: Optional[str] = Field(None, description="Credential ID or certificate number")
    url: Optional[str] = Field(None, description="Certificate verification URL")
    
    @validator('issue_date', 'expiry_date')
    def validate_dates(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m')
            except ValueError:
                raise ValueError('Date must be in YYYY-MM format')
        return v
    
    @validator('url')
    def validate_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class Project(BaseModel):
    """Project entry in user profile."""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    skills: List[str] = Field(default_factory=list, description="Skills used in project")
    links: List[str] = Field(default_factory=list, description="Project links (GitHub, demo, etc.)")
    
    @validator('links')
    def validate_links(cls, v):
        # Basic URL validation
        for link in v:
            if not (link.startswith('http://') or link.startswith('https://')):
                raise ValueError(f'Invalid URL: {link}')
        return v


class Internship(BaseModel):
    """Internship entry in user profile."""
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Role/position")
    duration_months: int = Field(..., description="Duration in months")
    skills: List[str] = Field(default_factory=list, description="Skills used")
    description: Optional[str] = Field(None, description="Internship description")
    
    @validator('duration_months')
    def validate_duration(cls, v):
        if v <= 0 or v > 24:
            raise ValueError('Duration must be between 1 and 24 months')
        return v


class ProofPack(BaseModel):
    """Proof entry for verification."""
    type: str = Field(..., description="Type of proof (github, portfolio, certificate, etc.)")
    url: str = Field(..., description="URL to proof")
    supports: List[str] = Field(default_factory=list, description="What this proof supports (project names, skills, etc.)")
    
    @validator('url')
    def validate_url(cls, v):
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class Constraints(BaseModel):
    """Application constraints and preferences."""
    location: List[str] = Field(default_factory=list, description="Preferred locations (remote, cities, countries)")
    visa_required: bool = Field(False, description="Whether visa sponsorship is required")
    start_date: Optional[str] = Field(None, description="Preferred start date (YYYY-MM format)")
    blocked_companies: List[str] = Field(default_factory=list, description="Companies to never apply to")
    max_apps_per_day: int = Field(5, description="Maximum applications per day")
    min_match_score: float = Field(0.6, description="Minimum match score to apply")
    
    @validator('max_apps_per_day')
    def validate_max_apps(cls, v):
        if v <= 0 or v > 50:
            raise ValueError('Max applications per day must be between 1 and 50')
        return v
    
    @validator('min_match_score')
    def validate_min_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Min match score must be between 0.0 and 1.0')
        return v
    
    @validator('start_date')
    def validate_start_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m')
            except ValueError:
                raise ValueError('Start date must be in YYYY-MM format')
        return v


class UserProfile(BaseModel):
    """
    User Profile - SINGLE SOURCE OF TRUTH
    This is the authoritative profile structure for persistent user profiles.
    """
    student_id: str = Field(..., description="Unique student identifier")
    basic_info: BasicInfo = Field(..., description="Basic personal information")
    skill_vocab: List[str] = Field(..., description="Complete vocabulary of all skills")
    education: List[Education] = Field(default_factory=list, description="Education history")
    projects: List[Project] = Field(default_factory=list, description="Project portfolio")
    internships: List[Internship] = Field(default_factory=list, description="Internship experience")
    certificates: List[Certificate] = Field(default_factory=list, description="Certifications and credentials")
    skills: List[str] = Field(default_factory=list, description="Primary skills (subset of skill_vocab)")
    proof_pack: List[ProofPack] = Field(default_factory=list, description="Verification proofs")
    constraints: Constraints = Field(default_factory=Constraints, description="Application constraints")
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp")
    
    @validator('skill_vocab')
    def validate_skill_vocab_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("skill_vocab must contain only unique skills")
        return v
    
    @validator('skills')
    def validate_skills_in_vocab(cls, v, values):
        if 'skill_vocab' in values:
            skill_vocab_set = set(values['skill_vocab'])
            for skill in v:
                if skill not in skill_vocab_set:
                    raise ValueError(f"Skill '{skill}' is not in skill_vocab")
        return v
    
    @validator('projects')
    def validate_project_skills(cls, v, values):
        if 'skill_vocab' in values:
            skill_vocab_set = set(values['skill_vocab'])
            for project in v:
                for skill in project.skills:
                    if skill not in skill_vocab_set:
                        raise ValueError(f"Project skill '{skill}' in project '{project.name}' is not in skill_vocab")
        return v
    
    @validator('internships')
    def validate_internship_skills(cls, v, values):
        if 'skill_vocab' in values:
            skill_vocab_set = set(values['skill_vocab'])
            for internship in v:
                for skill in internship.skills:
                    if skill not in skill_vocab_set:
                        raise ValueError(f"Internship skill '{skill}' is not in skill_vocab")
        return v