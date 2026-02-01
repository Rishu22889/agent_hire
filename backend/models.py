"""
Pydantic models for the persistent job application platform API.
These are separate from the core schemas to maintain separation of concerns.
"""
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


# ==================== ARTIFACT APPROVAL WORKFLOW ====================

class UserConfirmation(BaseModel):
    """User confirmation data for artifact approval."""
    bullets_verified: List[Dict[str, Any]] = Field(..., description="List of bullet verification confirmations")
    accuracy_confirmed: bool = Field(..., description="User confirmed accuracy checkbox")
    confirmation_timestamp: str = Field(..., description="When user confirmed (ISO format)")
    
    @validator('confirmation_timestamp', pre=True)
    def validate_timestamp(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class ArtifactSnapshot(BaseModel):
    """
    Immutable, approved version of StudentArtifactPack with audit metadata.
    Once created, this cannot be modified (frozen: true).
    """
    id: str = Field(..., description="Unique snapshot identifier")
    user_id: int = Field(..., description="User who owns this snapshot")
    student_artifact_pack: Dict[str, Any] = Field(..., description="Frozen StudentArtifactPack data")
    approved_at: datetime = Field(default_factory=datetime.utcnow, description="When this was approved")
    source_resume_hash: str = Field(..., description="Hash of source resume for traceability")
    source_profile_hash: str = Field(..., description="Hash of source UserProfile for traceability")
    frozen: bool = Field(True, description="Always true - indicates immutability")
    approval_metadata: Dict[str, Any] = Field(..., description="User confirmation and verification metadata")
    
    @validator('frozen')
    def validate_frozen_always_true(cls, v):
        if not v:
            raise ValueError('ArtifactSnapshot must always be frozen (frozen: true)')
        return v
    
    @validator('student_artifact_pack')
    def validate_student_artifact_pack_structure(cls, v):
        # Basic validation - ensure required fields exist
        required_fields = ['source_resume_hash', 'skill_vocab', 'education', 'projects']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'StudentArtifactPack missing required field: {field}')
        
        # Validate all bullets are verified
        for project in v.get('projects', []):
            for bullet in project.get('bullets', []):
                if not bullet.get('verified', False):
                    raise ValueError('All bullets in approved ArtifactSnapshot must be verified: true')
        
        return v
    
    @validator('approval_metadata')
    def validate_approval_metadata(cls, v):
        required_fields = ['user_confirmation', 'verification_count']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Approval metadata missing required field: {field}')
        return v
    
    def generate_integrity_hash(self) -> str:
        """Generate cryptographic hash for integrity verification."""
        content = f"{self.user_id}:{self.source_resume_hash}:{self.approved_at.isoformat()}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class DraftArtifactPack(BaseModel):
    """
    Generated but unapproved StudentArtifactPack with verified: false enforcement.
    This is the intermediate state before user approval.
    """
    student_artifact_pack: Dict[str, Any] = Field(..., description="Draft StudentArtifactPack structure")
    status: str = Field("DRAFT", description="Always 'DRAFT' to indicate not approved")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When this draft was created")
    source_profile_hash: str = Field(..., description="Hash of source UserProfile for traceability")
    
    @validator('status')
    def validate_status_is_draft(cls, v):
        if v != "DRAFT":
            raise ValueError('DraftArtifactPack status must always be "DRAFT"')
        return v
    
    @validator('student_artifact_pack')
    def validate_no_verified_bullets(cls, v):
        # Ensure no bullets are marked as verified in draft
        for project in v.get('projects', []):
            for bullet in project.get('bullets', []):
                if bullet.get('verified', False):
                    raise ValueError('Draft artifacts cannot contain verified: true bullets')
        return v


# ==================== AUTHENTICATION ====================

class UserRegistrationRequest(BaseModel):
    """Request to register a new user."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserLoginRequest(BaseModel):
    """Request to login a user."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Authentication response."""
    success: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    token: Optional[str] = None
    message: str


# ==================== RESUME & PROFILE ====================

class ResumeUploadResponse(BaseModel):
    """Response for resume upload."""
    success: bool
    resume_hash: str
    extracted_text: str
    message: str


class DraftProfileRequest(BaseModel):
    """Request to generate draft profile from resume."""
    resume_text: str
    user_id: int


class DraftProfileResponse(BaseModel):
    """Response containing draft profile."""
    success: bool
    draft_profile: Optional[Dict[str, Any]] = None
    extraction_explanation: Optional[str] = None
    error: Optional[str] = None


class SaveProfileRequest(BaseModel):
    """Request to save user profile."""
    user_id: int
    profile_data: Dict[str, Any]


class SaveProfileResponse(BaseModel):
    """Response for saving profile."""
    success: bool
    message: str
    profile_id: Optional[int] = None


class ProfileValidationResponse(BaseModel):
    """Response for profile validation."""
    success: bool
    message: str
    errors: Optional[Dict[str, str]] = None


# ==================== JOB LISTINGS ====================

class JobListingRequest(BaseModel):
    """Request to add a job listing."""
    job_id: str
    company: str
    role: str
    location: str
    required_skills: List[str]
    min_experience_years: int
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = "full-time"
    posted_date: Optional[str] = None
    expires_date: Optional[str] = None


class JobListingResponse(BaseModel):
    """Job listing response."""
    job_id: str
    company: str
    role: str
    location: str
    required_skills: List[str]
    min_experience_years: int
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: str
    posted_date: Optional[str] = None
    expires_date: Optional[str] = None
    created_at: str


class JobListingsResponse(BaseModel):
    """Response containing multiple job listings."""
    success: bool
    jobs: List[JobListingResponse]
    total_count: int


# ==================== AUTOPILOT ====================

class RunAutopilotRequest(BaseModel):
    """Request to run autopilot."""
    user_id: int
    job_ids: Optional[List[str]] = None  # If None, run on all eligible jobs


class RunAutopilotResponse(BaseModel):
    """Response for autopilot run."""
    success: bool
    run_id: Optional[int] = None
    message: str
    error: Optional[str] = None


class AutopilotStatusResponse(BaseModel):
    """Response for autopilot status."""
    run_id: int
    status: str
    job_ids: List[str]
    summary_data: Dict[str, Any]
    started_at: str
    completed_at: Optional[str] = None


# ==================== APPLICATION HISTORY ====================

class ApplicationHistoryEntry(BaseModel):
    """Individual application history entry."""
    id: int
    run_id: int
    job_id: str
    company: str
    role: str
    status: str
    skip_reason: Optional[str] = None
    receipt_id: Optional[str] = None
    timestamp: float
    created_at: str


class ApplicationHistoryResponse(BaseModel):
    """Response containing application history."""
    success: bool
    history: List[ApplicationHistoryEntry]
    total_count: int
    stats: Dict[str, int]


class DeleteHistoryRequest(BaseModel):
    """Request to delete history entry."""
    user_id: int
    history_id: int


# ==================== DASHBOARD ====================

class UserDashboardResponse(BaseModel):
    """Dashboard data response."""
    success: bool
    user_profile: Dict[str, Any]
    recent_runs: List[AutopilotStatusResponse]
    application_stats: Dict[str, int]
    recent_applications: List[ApplicationHistoryEntry]


# ==================== ARTIFACT WORKFLOW ENDPOINTS ====================

class GenerateDraftRequest(BaseModel):
    """Request to generate draft artifacts from UserProfile."""
    user_id: int = Field(..., description="User ID")


class GenerateDraftResponse(BaseModel):
    """Response containing draft artifacts."""
    success: bool
    draft_artifact_pack: Optional[DraftArtifactPack] = None
    message: str
    error: Optional[str] = None


class ApproveArtifactsRequest(BaseModel):
    """Request to approve draft artifacts."""
    user_id: int = Field(..., description="User ID")
    draft_artifact_pack: DraftArtifactPack = Field(..., description="Draft to approve")
    user_confirmation: UserConfirmation = Field(..., description="User confirmation data")


class ApproveArtifactsResponse(BaseModel):
    """Response for artifact approval."""
    success: bool
    artifact_snapshot_id: Optional[str] = None
    message: str
    error: Optional[str] = None


class CurrentArtifactsResponse(BaseModel):
    """Response containing current approved artifacts."""
    success: bool
    artifact_snapshot: Optional[ArtifactSnapshot] = None
    message: str


# ==================== BULK OPERATIONS ====================

class BulkJobUploadRequest(BaseModel):
    """Request to upload multiple job listings."""
    jobs: List[JobListingRequest]


class BulkJobUploadResponse(BaseModel):
    """Response for bulk job upload."""
    success: bool
    uploaded_count: int
    failed_count: int
    errors: List[str]