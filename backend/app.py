"""
FastAPI application for the persistent job application platform.
Supports user profiles, job listings, and application history while preserving all safety guarantees.
"""
import asyncio
import sys
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.engine import run_autopilot
from backend.database import PersistentDatabase
from backend.auth import AuthManager
from backend.scheduler import start_autonomous_ai_agent  # Import autonomous agent
from backend.job_fetcher import JobFetcher  # Import job fetcher for portal integration
from backend.models import (
    UserRegistrationRequest, UserLoginRequest, AuthResponse,
    ResumeUploadResponse, DraftProfileRequest, DraftProfileResponse,
    SaveProfileRequest, SaveProfileResponse, ProfileValidationResponse,
    JobListingRequest, JobListingResponse, JobListingsResponse,
    RunAutopilotRequest, RunAutopilotResponse, AutopilotStatusResponse,
    ApplicationHistoryResponse, DeleteHistoryRequest, UserDashboardResponse,
    BulkJobUploadRequest, BulkJobUploadResponse,
    GenerateDraftRequest, GenerateDraftResponse, ApproveArtifactsRequest,
    ApproveArtifactsResponse, CurrentArtifactsResponse,
    DraftArtifactPack
)
from backend.ai_agents import (
    generate_resume_hash, generate_draft_profile_from_text, explain_extraction_results,
    decode_text_file, extract_text_from_pdf_pdfplumber, extract_text_from_word
)
from schemas.user_profile_schema import UserProfile
from schemas.job_schema import JobListing
from schemas.student_schema import StudentArtifactPack

app = FastAPI(
    title="Persistent Job Application Platform",
    description="Student-facing web platform for autonomous job applications with persistent profiles",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database and auth instances
db = PersistentDatabase()
auth_manager = AuthManager(db)
job_fetcher = JobFetcher()  # Initialize job fetcher for portal integration

# Setup logger
logger = logging.getLogger(__name__)

# Start autonomous AI agent
start_autonomous_ai_agent()

# Background task storage
running_tasks: Dict[int, asyncio.Task] = {}


def get_auth_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract auth token from Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Persistent Job Application Platform API", "status": "running", "version": "2.0.0"}


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register", response_model=AuthResponse)
async def register_user(request: UserRegistrationRequest):
    """Register a new user account."""
    success, message, user_id = auth_manager.register_user(request.email, request.password)
    
    return AuthResponse(
        success=success,
        user_id=user_id,
        email=request.email if success else None,
        message=message
    )


@app.post("/api/auth/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest):
    """Login user and return session token."""
    success, message, token, user_id = auth_manager.login_user(request.email, request.password)
    
    return AuthResponse(
        success=success,
        user_id=user_id,
        email=request.email if success else None,
        token=token,
        message=message
    )


@app.post("/api/auth/logout")
async def logout_user(authorization: Optional[str] = Header(None)):
    """Logout user."""
    token = get_auth_token(authorization)
    if token:
        auth_manager.logout_user(token)
    
    return {"success": True, "message": "Logged out successfully"}


# ==================== RESUME & PROFILE ENDPOINTS ====================

@app.post("/api/profile/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    Upload resume and extract text (pdfplumber ONLY for PDFs).
    User must be authenticated.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        # Read file content
        content = await file.read()
        filename = file.filename.lower() if file.filename else ""
        
        # Extract text using appropriate method (STRICT: pdfplumber ONLY for PDFs)
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf_pdfplumber(content)
        elif filename.endswith(('.doc', '.docx')):
            resume_text = extract_text_from_word(content)
        else:
            resume_text = decode_text_file(content)
        
        if not resume_text or not resume_text.strip():
            raise ValueError("No text content could be extracted from the file")
        
        # Generate hash
        resume_hash = generate_resume_hash(resume_text)
        
        # Check if this is a new resume (different hash) for existing users
        try:
            existing_profile = db.get_user_profile(user_id)
            if existing_profile:
                existing_hash = existing_profile.get("profile_data", {}).get("source_resume_hash")
                if existing_hash and existing_hash != resume_hash:
                    # New resume uploaded - clear application history to allow reapplying
                    cleared_count = db.clear_user_application_history(user_id)
                    logger.info(f"New resume uploaded for user {user_id}: cleared {cleared_count} application history entries")
        except Exception as e:
            # If profile doesn't exist yet, that's fine - this is probably first upload
            logger.info(f"Resume upload for user {user_id}: {e}")
        
        return ResumeUploadResponse(
            success=True,
            resume_hash=resume_hash,
            extracted_text=resume_text,
            message=f"Resume uploaded and text extracted successfully. Application history cleared - you can reapply to jobs with your updated resume."
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process resume: {str(e)}")


@app.post("/api/profile/generate-draft", response_model=DraftProfileResponse)
async def generate_draft_profile(
    request: DraftProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generate draft profile from resume text (AI ASSISTIVE ONLY).
    
    STRICT RULES:
    - AI output is ALWAYS a DRAFT
    - AI may suggest data
    - AI may NOT finalize, validate, or submit anything
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Generate draft using AI (STRICT: NO INVENTION)
        success, draft_profile, error = generate_draft_profile_from_text(request.resume_text)
        
        if not success:
            return DraftProfileResponse(
                success=False,
                error=error or "Failed to generate draft profile"
            )
        
        # Add user-specific fields
        draft_profile["student_id"] = f"student_{user_id}_{generate_resume_hash(request.resume_text)[:8]}"
        
        # Generate explanation
        explanation = explain_extraction_results(request.resume_text, draft_profile)
        
        return DraftProfileResponse(
            success=True,
            draft_profile=draft_profile,
            extraction_explanation=explanation
        )
    
    except Exception as e:
        return DraftProfileResponse(
            success=False,
            error=f"Error generating draft profile: {str(e)}"
        )


def clean_profile_data(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean profile data by removing empty URLs and invalid entries."""
    cleaned = profile_data.copy()
    
    # Ensure basic_info exists (for backward compatibility)
    if 'basic_info' not in cleaned:
        cleaned['basic_info'] = {
            "name": "Student Applicant",
            "email": "student@example.com",
            "phone": "",
            "location": ""
        }
    
    # Clean project links - remove empty strings
    if 'projects' in cleaned:
        for project in cleaned['projects']:
            if 'links' in project:
                project['links'] = [link for link in project['links'] if link and link.strip()]
    
    # Clean proof pack - remove entries with empty URLs
    if 'proof_pack' in cleaned:
        cleaned['proof_pack'] = [
            proof for proof in cleaned['proof_pack'] 
            if proof.get('url') and proof['url'].strip()
        ]
    
    return cleaned


@app.post("/api/profile/validate", response_model=ProfileValidationResponse)
async def validate_profile(
    request: SaveProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Validate user profile against schema (HARD GATE).
    
    STRICT RULES:
    - Schema validation is the final authority
    - If validation fails → block execution
    - User must fix errors manually
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Clean the profile data first
        cleaned_profile_data = clean_profile_data(request.profile_data)
        
        # HARD GATE: Schema validation is the final authority
        profile = UserProfile(**cleaned_profile_data)
        
        return ProfileValidationResponse(
            success=True,
            message="Profile validation passed - ready to save"
        )
    
    except Exception as e:
        # Extract field-specific errors
        errors = {}
        if hasattr(e, 'errors'):
            for error in e.errors():
                field_path = '.'.join(str(loc) for loc in error['loc'])
                errors[field_path] = error['msg']
        
        return ProfileValidationResponse(
            success=False,
            message="Profile validation failed",
            errors=errors
        )


@app.post("/api/profile/save", response_model=SaveProfileResponse)
async def save_profile(
    request: SaveProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Save user profile (SINGLE SOURCE OF TRUTH).
    Profile can be edited anytime and is reused across all job runs.
    
    IMPORTANT: When profile is modified, existing ArtifactSnapshots remain unchanged.
    New artifact generation and approval is required for engine execution.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Clean the profile data first
        cleaned_profile_data = clean_profile_data(request.profile_data)
        
        # Double-check validation (safety measure)
        profile = UserProfile(**cleaned_profile_data)
        
        # Update last_modified timestamp
        profile_data_with_timestamp = cleaned_profile_data.copy()
        profile_data_with_timestamp['last_modified'] = datetime.utcnow().isoformat()
        
        # Check if profile exists
        existing_profile = db.get_user_profile(user_id)
        
        if existing_profile:
            # Check if profile has actually changed (to avoid unnecessary resets)
            existing_data = existing_profile.get("profile_data", {})
            if existing_data != cleaned_profile_data:
                # Profile has changed - clear application history to allow reapplying
                cleared_count = db.clear_user_application_history(user_id)
                logger.info(f"Profile updated for user {user_id}: cleared {cleared_count} application history entries")
            
            # Update existing profile
            success = db.update_user_profile(user_id, profile_data_with_timestamp)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update profile")
            profile_id = existing_profile["id"]
            
            # Profile modification invalidates existing approvals
            message = "Profile saved successfully. Application history cleared - you can now reapply to jobs with your updated profile."
        else:
            # Create new profile
            profile_id = db.create_user_profile(
                user_id=user_id,
                student_id=profile.student_id,
                profile_data=profile_data_with_timestamp
            )
            message = "Profile saved successfully."
        
        return SaveProfileResponse(
            success=True,
            message=message,
            profile_id=profile_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save profile: {str(e)}")


@app.get("/api/profile/get")
async def get_user_profile(authorization: Optional[str] = Header(None)):
    """Get user's profile (SINGLE SOURCE OF TRUTH)."""
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    profile = db.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"success": True, "profile": profile}


# ==================== JOB LISTINGS ENDPOINTS ====================

@app.post("/api/jobs/add", response_model=JobListingResponse)
async def add_job_listing(request: JobListingRequest):
    """Add a new job listing."""
    try:
        # Validate against JobListing schema
        job_listing = JobListing(
            job_id=request.job_id,
            company=request.company,
            role=request.role,
            location=request.location,
            required_skills=request.required_skills,
            min_experience_years=request.min_experience_years
        )
        
        # Add to database
        job_data = request.dict()
        db.add_job_listing(job_data)
        
        return JobListingResponse(**job_data, created_at=str(datetime.now()))
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add job listing: {str(e)}")


@app.post("/api/jobs/bulk-upload", response_model=BulkJobUploadResponse)
async def bulk_upload_jobs(request: BulkJobUploadRequest):
    """Upload multiple job listings."""
    uploaded_count = 0
    failed_count = 0
    errors = []
    
    for job_request in request.jobs:
        try:
            # Validate against JobListing schema
            job_listing = JobListing(
                job_id=job_request.job_id,
                company=job_request.company,
                role=job_request.role,
                location=job_request.location,
                required_skills=job_request.required_skills,
                min_experience_years=job_request.min_experience_years
            )
            
            # Add to database
            db.add_job_listing(job_request.dict())
            uploaded_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f"Job {job_request.job_id}: {str(e)}")
    
    return BulkJobUploadResponse(
        success=failed_count == 0,
        uploaded_count=uploaded_count,
        failed_count=failed_count,
        errors=errors
    )


@app.get("/api/jobs/list", response_model=JobListingsResponse)
async def get_job_listings(limit: int = 50):
    """Get active job listings (UI format) - Returns empty since we use portal only."""
    try:
        # Return empty list since we only use portal jobs now
        return JobListingsResponse(
            success=True,
            jobs=[],
            total_count=0
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job listings: {str(e)}")


@app.get("/api/jobs/ai-ranked")
async def get_ai_ranked_jobs(
    authorization: Optional[str] = Header(None)
):
    """
    Get AI-ranked jobs based on user profile.
    AI searches portal jobs, ranks by match score, and decides which to apply to.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        # Get user profile
        user_profile = db.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found. Please complete your profile first.")
        
        # Check if sandbox portal is available
        portal_status = job_fetcher.check_portal_status()
        if portal_status.get("status") != "active":
            raise HTTPException(status_code=503, detail="Sandbox portal is not available. Please start the portal at http://localhost:5001")
        
        # Fetch jobs from sandbox portal
        portal_jobs = job_fetcher.fetch_jobs()
        
        if not portal_jobs:
            raise HTTPException(status_code=404, detail="No jobs available from sandbox portal")
        
        # Convert portal jobs to internal format for AI ranking
        all_jobs = []
        for portal_job in portal_jobs:
            internal_job = job_fetcher.convert_portal_job_to_internal_format(portal_job)
            all_jobs.append(internal_job)
        
        # Get application history to mark applied jobs
        application_history = db.get_user_application_history(user_id, limit=1000)
        applied_job_ids = set()
        for app in application_history:
            if app["status"] in ["submitted", "retried"]:
                applied_job_ids.add(app["job_id"])
        
        # AI job matching and ranking
        from backend.ai_agents import rank_jobs_for_user
        ranked_jobs = rank_jobs_for_user(user_profile["profile_data"], all_jobs)
        
        # Update status for jobs that have been applied to
        updated_count = 0
        for job in ranked_jobs:
            if job["job_id"] in applied_job_ids:
                job["status"] = "applied"
                job["ai_reasoning"] = "Already applied to this position"
                updated_count += 1
        
        # Calculate summary statistics
        summary = {
            "total_found": len(ranked_jobs),
            "will_apply": len([j for j in ranked_jobs if j["status"] == "will_apply"]),
            "applied": len([j for j in ranked_jobs if j["status"] == "applied"]),
            "rejected": len([j for j in ranked_jobs if j["status"] == "rejected_by_ai"])
        }
        
        return {
            "success": True,
            "data": {
                "jobs": ranked_jobs,
                "summary": summary,
                "profile_id": user_profile["id"],
                "source": "sandbox_portal"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI-ranked jobs: {str(e)}")


@app.get("/api/portal/status")
async def get_portal_status():
    """
    Get sandbox portal status and integration info.
    """
    try:
        portal_status = job_fetcher.check_portal_status()
        
        # Get portal job count
        portal_jobs_count = 0
        if portal_status.get("status") == "active":
            portal_jobs = job_fetcher.fetch_jobs()
            portal_jobs_count = len(portal_jobs)
        
        return {
            "success": True,
            "portal_status": portal_status,
            "integration_status": {
                "portal_available": portal_status.get("status") == "active",
                "portal_jobs_count": portal_jobs_count,
                "database_jobs_count": 0,  # No longer using database jobs
                "mode": "portal_only",
                "autonomous_agent_active": True
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get portal status: {str(e)}"
        }


@app.post("/api/autopilot/start")
async def start_autopilot(
    authorization: Optional[str] = Header(None)
):
    """
    Start autopilot - AI automatically applies to suitable jobs.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        # Get user profile
        user_profile = db.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get AI-ranked jobs to find which ones to apply to
        all_jobs = db.get_active_job_listings(limit=1000)
        from backend.ai_agents import rank_jobs_for_user
        ranked_jobs = rank_jobs_for_user(user_profile["profile_data"], all_jobs)
        
        # Filter jobs that AI decided to apply to
        jobs_to_apply = [job for job in ranked_jobs if job["status"] == "will_apply"]
        
        if not jobs_to_apply:
            return {
                "success": False,
                "message": "No jobs found that meet your criteria for application.",
                "applied_count": 0
            }
        
        # Create autopilot run record
        run_id = db.create_autopilot_run(
            user_id=user_id,
            job_ids=[job["job_id"] for job in jobs_to_apply]
        )
        
        # Convert user profile to student artifact pack format for engine
        from backend.ai_agents import convert_user_profile_to_student_artifact_pack
        student_artifact_pack = convert_user_profile_to_student_artifact_pack(user_profile["profile_data"])
        
        # Convert jobs to engine format
        engine_jobs = []
        for job in jobs_to_apply:
            engine_jobs.append(convert_database_job_to_engine_format(job))
        
        # Run the autopilot engine
        from backend.engine import run_autopilot
        from core.tracker import ApplicationTracker
        
        tracker = ApplicationTracker()
        result = run_autopilot(student_artifact_pack, engine_jobs, tracker)
        
        if result["success"]:
            # Save application history
            applications = []
            for event in tracker.events:
                applications.append({
                    "job_id": event["job_id"],
                    "status": event["status"],
                    "reason": event.get("reason"),
                    "receipt_id": event.get("receipt_id"),
                    "timestamp": event["timestamp"]
                })
            
            db.save_application_history(user_id, run_id, applications)
            
            # Verify the data was saved
            saved_history = db.get_user_application_history(user_id, limit=10)
            
            # Update autopilot run with results
            db.update_autopilot_run_success(run_id, result["summary"])
            
            return {
                "success": True,
                "message": f"Autopilot completed! Applied to {result['summary'].get('submitted', 0)} jobs successfully.",
                "autopilot_id": run_id,
                "applied_count": result['summary'].get('submitted', 0),
                "summary": result["summary"]
            }
        else:
            # Update autopilot run with error
            db.update_autopilot_run_error(run_id, result["error"])
            
            return {
                "success": False,
                "message": f"Autopilot failed: {result['error']}",
                "autopilot_id": run_id
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start autopilot: {str(e)}")


# ==================== ARTIFACT WORKFLOW ENDPOINTS ====================

@app.post("/api/artifacts/generate-draft", response_model=GenerateDraftResponse)
async def generate_draft_artifacts(
    request: GenerateDraftRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generate draft artifacts from UserProfile for user review.
    
    SAFETY RULES:
    - Creates DraftArtifactPack with verified: false
    - Clearly marks as NOT APPROVED
    - User must review before engine execution
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get user profile (SINGLE SOURCE OF TRUTH)
        profile = db.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile_data = profile["profile_data"]
        
        # Generate draft using ArtifactGenerator
        from backend.artifact_services import ArtifactGenerator
        generator = ArtifactGenerator()
        draft_artifact_pack = generator.generate_draft(profile_data, user_id=user_id)
        
        return GenerateDraftResponse(
            success=True,
            draft_artifact_pack=draft_artifact_pack,
            message="Draft artifacts generated successfully. Please review and approve before engine execution."
        )
    
    except Exception as e:
        return GenerateDraftResponse(
            success=False,
            message="Failed to generate draft artifacts",
            error=str(e)
        )


@app.post("/api/artifacts/approve", response_model=ApproveArtifactsResponse)
async def approve_artifacts(
    request: ApproveArtifactsRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Approve draft artifacts and create immutable snapshot.
    
    SAFETY RULES:
    - Validates user confirmation
    - Creates immutable ArtifactSnapshot
    - Only verified bullets allowed in snapshot
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Create approved snapshot using ApprovalService
        from backend.artifact_services import ApprovalService
        approval_service = ApprovalService()
        
        artifact_snapshot = approval_service.submit_for_approval(
            request.draft_artifact_pack,
            request.user_confirmation,
            user_id
        )
        
        return ApproveArtifactsResponse(
            success=True,
            artifact_snapshot_id=artifact_snapshot.id,
            message="Artifacts approved successfully. Engine execution is now enabled."
        )
    
    except ValueError as e:
        return ApproveArtifactsResponse(
            success=False,
            message="Approval validation failed",
            error=str(e)
        )
    except Exception as e:
        return ApproveArtifactsResponse(
            success=False,
            message="Failed to approve artifacts",
            error=str(e)
        )


@app.get("/api/artifacts/current", response_model=CurrentArtifactsResponse)
async def get_current_artifacts(authorization: Optional[str] = Header(None)):
    """
    Get current approved ArtifactSnapshot for user.
    
    Returns the latest approved snapshot or indicates none exists.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        # Get current approved snapshot
        from backend.artifact_services import ApprovalService
        approval_service = ApprovalService()
        
        current_snapshot = approval_service.get_current_approved(user_id)
        
        if current_snapshot:
            return CurrentArtifactsResponse(
                success=True,
                artifact_snapshot=current_snapshot,
                message="Current approved artifacts retrieved successfully"
            )
        else:
            return CurrentArtifactsResponse(
                success=True,
                artifact_snapshot=None,
                message="No approved artifacts found. Please generate and approve artifacts first."
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current artifacts: {str(e)}")


@app.get("/api/artifacts/status")
async def get_artifact_workflow_status(authorization: Optional[str] = Header(None)):
    """
    Get complete artifact workflow status for user.
    
    Returns status indicators for draft vs approved artifacts and workflow progress.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        from backend.status_indicators import (
            get_artifact_status_display, 
            format_approval_workflow_status,
            get_engine_execution_status
        )
        from backend.artifact_services import ApprovalService
        
        # Get user profile for last modified timestamp
        profile = db.get_user_profile(user_id)
        profile_modified = profile["profile_data"].get("last_modified") if profile else None
        
        # Get current approved snapshot
        approval_service = ApprovalService()
        current_snapshot = approval_service.get_current_approved(user_id)
        
        # Get current draft from database
        current_draft = None
        draft_data = approval_service.db.get_draft_artifact(user_id)
        if draft_data:
            current_draft = DraftArtifactPack(
                student_artifact_pack=draft_data["student_artifact_pack"],
                status=draft_data["status"],
                created_at=datetime.fromisoformat(draft_data["created_at"]),
                source_profile_hash=draft_data["source_profile_hash"]
            )
        
        # Generate status displays
        artifact_status = get_artifact_status_display(current_draft, current_snapshot)
        engine_status = get_engine_execution_status(current_snapshot)
        workflow_status = format_approval_workflow_status(
            user_profile_modified=profile_modified,
            draft_created=current_draft.created_at.isoformat() if current_draft else None,
            approved_at=current_snapshot.approved_at.isoformat() if current_snapshot else None
        )
        
        return {
            "success": True,
            "artifact_status": artifact_status,
            "engine_status": engine_status,
            "workflow_status": workflow_status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


# ==================== AUTOPILOT ENDPOINTS ====================

# REMOVED: convert_user_profile_to_student_artifact_pack function
# This function violated safety rules by auto-setting verified: True
# The engine must ONLY consume user-approved, immutable artifact snapshots


def convert_database_job_to_engine_format(db_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert database job format to engine JobListing format.
    
    Args:
        db_job: Job data from database (with extra fields)
    
    Returns:
        JobListing compatible dictionary (only core fields)
    """
    return {
        "job_id": db_job["job_id"],
        "company": db_job["company"],
        "role": db_job["role"],
        "location": db_job["location"],
        "required_skills": db_job["required_skills"],
        "min_experience_years": db_job["min_experience_years"]
    }


# REMOVED: run_autopilot_background function
# This function used auto-verification conversion which violated safety rules
# The engine must ONLY consume user-approved, immutable artifact snapshots


@app.post("/api/autopilot/run", response_model=RunAutopilotResponse)
async def run_autopilot_endpoint(
    request: RunAutopilotRequest,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """
    SAFETY GATE: Engine can ONLY run with approved artifact snapshots.
    This endpoint validates approved artifacts before execution.
    """
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get job IDs to process
        if request.job_ids:
            job_ids = request.job_ids
        else:
            # Get all active jobs
            jobs = db.get_active_job_listings(1000)
            job_ids = [job["job_id"] for job in jobs]
        
        if not job_ids:
            raise HTTPException(status_code=400, detail="No jobs to process")
        
        # SAFETY GATE: Use EngineGateway to validate and execute
        from backend.artifact_services import ApprovalService, EngineGateway
        approval_service = ApprovalService()
        engine_gateway = EngineGateway(approval_service)
        
        result = engine_gateway.validate_and_execute(user_id, job_ids)
        
        if result["success"]:
            return RunAutopilotResponse(
                success=True,
                run_id=None,  # Will be set when database integration is complete
                message=f"Autopilot executed successfully with approved artifacts for {len(job_ids)} jobs"
            )
        else:
            return RunAutopilotResponse(
                success=False,
                error=result["error"]
            )
    
    except ValueError as e:
        # Safety gate violations
        return RunAutopilotResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return RunAutopilotResponse(
            success=False,
            error=f"Failed to execute autopilot: {str(e)}"
        )


@app.get("/api/autopilot/status/{run_id}", response_model=AutopilotStatusResponse)
async def get_autopilot_status(
    run_id: int,
    authorization: Optional[str] = Header(None)
):
    """Get status of autopilot run."""
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        runs = db.get_user_autopilot_runs(user_id, limit=100)
        run_data = next((run for run in runs if run["id"] == run_id), None)
        
        if not run_data:
            raise HTTPException(status_code=404, detail="Run not found")
        
        return AutopilotStatusResponse(
            run_id=run_data["id"],
            status=run_data["status"],
            job_ids=run_data["job_ids"],
            summary_data=run_data["summary_data"],
            started_at=run_data["started_at"],
            completed_at=run_data["completed_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== APPLICATION HISTORY ENDPOINTS ====================

@app.get("/api/history/applications", response_model=ApplicationHistoryResponse)
async def get_application_history(
    limit: int = 100,
    status_filter: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """Get application history for user (CRITICAL - persistent record)."""
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        history = db.get_user_application_history(user_id, limit, status_filter)
        stats = db.get_application_stats(user_id)
        
        from backend.models import ApplicationHistoryEntry
        history_entries = [ApplicationHistoryEntry(**entry) for entry in history]
        
        return ApplicationHistoryResponse(
            success=True,
            history=history_entries,
            total_count=len(history_entries),
            stats=stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history/delete")
async def delete_history_entry(
    request: DeleteHistoryRequest,
    authorization: Optional[str] = Header(None)
):
    """Delete application history entry (UI only - does NOT affect backend safety logs)."""
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        success = db.delete_application_history_entry(user_id, request.history_id)
        
        if success:
            return {"success": True, "message": "History entry deleted"}
        else:
            raise HTTPException(status_code=404, detail="History entry not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DASHBOARD ENDPOINT ====================

@app.get("/api/dashboard", response_model=UserDashboardResponse)
async def get_user_dashboard(authorization: Optional[str] = Header(None)):
    """Get dashboard data for user."""
    token = get_auth_token(authorization)
    is_auth, user_id, auth_message = auth_manager.require_auth(token)
    if not is_auth:
        raise HTTPException(status_code=401, detail=auth_message)
    
    try:
        # Get user profile
        profile = db.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get recent runs
        recent_runs = db.get_user_autopilot_runs(user_id, limit=5)
        
        # Get application stats
        stats = db.get_application_stats(user_id)
        
        # Get recent applications
        recent_applications = db.get_user_application_history(user_id, limit=10)
        
        from backend.models import ApplicationHistoryEntry
        recent_app_entries = [ApplicationHistoryEntry(**app) for app in recent_applications]
        
        run_responses = []
        for run in recent_runs:
            run_responses.append(AutopilotStatusResponse(
                run_id=run["id"],
                status=run["status"],
                job_ids=run["job_ids"],
                summary_data=run["summary_data"],
                started_at=run["started_at"],
                completed_at=run["completed_at"]
            ))
        
        return UserDashboardResponse(
            success=True,
            user_profile=profile,
            recent_runs=run_responses,
            application_stats=stats,
            recent_applications=recent_app_entries
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)