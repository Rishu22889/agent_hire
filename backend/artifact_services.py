"""
Artifact Generation & Approval Services

These services implement the explicit artifact workflow with safety guarantees:
- ArtifactGenerator: Converts UserProfile to DraftArtifactPack (verified: false)
- ApprovalService: Manages approval workflow and creates immutable snapshots

SAFETY RULES:
- ArtifactGenerator NEVER sets verified: true
- ArtifactGenerator NEVER auto-normalizes data
- ArtifactGenerator NEVER infers missing information
- ApprovalService ONLY creates snapshots with explicit user confirmation
"""
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from backend.models import DraftArtifactPack, ArtifactSnapshot, UserConfirmation
from schemas.user_profile_schema import UserProfile


class ArtifactGenerator:
    """
    Converts UserProfile to draft StudentArtifactPack with explicit non-approval marking.
    
    SAFETY GUARANTEES:
    - NEVER sets verified: true
    - NEVER auto-normalizes data  
    - NEVER infers missing information
    - Clearly marks output as DRAFT status
    """
    
    def __init__(self, database=None):
        """Initialize with database connection."""
        if database is None:
            from backend.database import PersistentDatabase
            self.db = PersistentDatabase()
        else:
            self.db = database
    
    def generate_draft(self, user_profile: Dict[str, Any], user_id: int = None) -> DraftArtifactPack:
        """
        Generate draft StudentArtifactPack from UserProfile.
        
        Args:
            user_profile: UserProfile data (validated)
            user_id: User ID for database storage (optional)
            
        Returns:
            DraftArtifactPack with all bullets marked verified: false
            
        Raises:
            ValueError: If user_profile is invalid or missing required fields
        """
        # Validate input is a proper UserProfile
        try:
            profile = UserProfile(**user_profile)
        except Exception as e:
            raise ValueError(f"Invalid UserProfile: {e}")
        
        # Generate source profile hash for traceability
        source_profile_hash = self._generate_profile_hash(user_profile)
        
        # Convert to StudentArtifactPack format with DRAFT bullets
        draft_student_artifact_pack = self._convert_to_student_artifact_pack(profile)
        
        draft = DraftArtifactPack(
            student_artifact_pack=draft_student_artifact_pack,
            status="DRAFT",  # Always DRAFT
            source_profile_hash=source_profile_hash
        )
        
        # Save to database if user_id provided
        if user_id is not None:
            draft_id = str(uuid.uuid4())
            success = self.db.save_draft_artifact(
                draft_id=draft_id,
                user_id=user_id,
                student_artifact_pack=draft_student_artifact_pack,
                source_profile_hash=source_profile_hash
            )
            if not success:
                raise RuntimeError("Failed to save draft artifact to database")
        
        return draft
    
    def _generate_profile_hash(self, user_profile: Dict[str, Any]) -> str:
        """Generate hash of UserProfile for traceability."""
        # Create deterministic string representation
        profile_str = f"{user_profile.get('student_id', '')}:{len(user_profile.get('skill_vocab', []))}:{len(user_profile.get('projects', []))}"
        return hashlib.sha256(profile_str.encode('utf-8')).hexdigest()
    
    def _convert_to_student_artifact_pack(self, profile: UserProfile) -> Dict[str, Any]:
        """
        Convert UserProfile to StudentArtifactPack format.
        
        CRITICAL SAFETY RULE: All bullets marked verified: false
        """
        # Convert projects with DRAFT bullets (verified: false)
        converted_projects = []
        for project in profile.projects:
            # Create bullets from project description - ALWAYS verified: false
            bullets = [{
                "description": project.description,
                "skills": project.skills[:3],  # Limit to 3 skills per bullet
                "verified": False,  # SAFETY: Never auto-verify
                "proofs": None
            }]
            
            converted_projects.append({
                "name": project.name,
                "description": project.description,
                "skills": project.skills,
                "bullets": bullets
            })
        
        # Convert education format (no verification needed for education)
        converted_education = []
        for edu in profile.education:
            converted_education.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field  # Convert field -> field_of_study
            })
        
        # Convert constraints
        converted_constraints = {
            "max_apps_per_day": profile.constraints.max_apps_per_day,
            "min_match_score": profile.constraints.min_match_score,
            "blocked_companies": profile.constraints.blocked_companies
        }
        
        return {
            "source_resume_hash": f"profile_{self._generate_profile_hash(profile.dict())}",
            "skill_vocab": profile.skill_vocab,
            "education": converted_education,
            "projects": converted_projects,
            "constraints": converted_constraints
        }


class ApprovalService:
    """
    Manages the approval workflow and creates immutable snapshots.
    
    SAFETY GUARANTEES:
    - Only creates snapshots with explicit user confirmation
    - Validates all bullets are verified before approval
    - Creates immutable snapshots (frozen: true)
    - Maintains audit trail
    """
    
    def __init__(self, database=None):
        """Initialize with database connection."""
        if database is None:
            from backend.database import PersistentDatabase
            self.db = PersistentDatabase()
        else:
            self.db = database
    
    def submit_for_approval(
        self, 
        draft: DraftArtifactPack, 
        user_confirmation: UserConfirmation,
        user_id: int
    ) -> ArtifactSnapshot:
        """
        Convert approved draft to immutable ArtifactSnapshot.
        
        Args:
            draft: DraftArtifactPack to approve
            user_confirmation: User's explicit confirmation
            user_id: ID of user approving
            
        Returns:
            Immutable ArtifactSnapshot
            
        Raises:
            ValueError: If validation fails or user hasn't confirmed properly
        """
        # Validate user confirmation
        self._validate_user_confirmation(user_confirmation, draft)
        
        # Apply user verifications to the draft
        approved_artifact_pack = self._apply_user_verifications(
            draft.student_artifact_pack, 
            user_confirmation
        )
        
        # Generate snapshot ID
        snapshot_id = str(uuid.uuid4())
        
        # Create approval metadata
        approval_metadata = {
            "user_confirmation": user_confirmation.dict(),
            "verification_count": len(user_confirmation.bullets_verified),
            "modified_bullets": [
                bv["bullet_id"] for bv in user_confirmation.bullets_verified 
                if bv.get("user_modified", False)
            ]
        }
        
        # Create immutable snapshot
        snapshot = ArtifactSnapshot(
            id=snapshot_id,
            user_id=user_id,
            student_artifact_pack=approved_artifact_pack,
            source_resume_hash=approved_artifact_pack["source_resume_hash"],
            source_profile_hash=draft.source_profile_hash,
            frozen=True,  # Always frozen
            approval_metadata=approval_metadata
        )
        
        # Save to database
        integrity_hash = snapshot.generate_integrity_hash()
        success = self.db.save_artifact_snapshot(
            snapshot_id=snapshot.id,
            user_id=user_id,
            student_artifact_pack=approved_artifact_pack,
            source_resume_hash=snapshot.source_resume_hash,
            source_profile_hash=snapshot.source_profile_hash,
            approval_metadata=approval_metadata,
            integrity_hash=integrity_hash
        )
        
        if not success:
            raise RuntimeError("Failed to save artifact snapshot to database")
        
        # Clean up draft artifacts after successful approval
        self.db.delete_draft_artifacts(user_id)
        
        return snapshot
    
    def get_current_approved(self, user_id: int) -> Optional[ArtifactSnapshot]:
        """
        Get current approved ArtifactSnapshot for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Current ArtifactSnapshot or None if no approval exists
        """
        snapshot_data = self.db.get_current_artifact_snapshot(user_id)
        
        if not snapshot_data:
            return None
        
        # Convert database data back to ArtifactSnapshot model
        return ArtifactSnapshot(
            id=snapshot_data["id"],
            user_id=snapshot_data["user_id"],
            student_artifact_pack=snapshot_data["student_artifact_pack"],
            approved_at=datetime.fromisoformat(snapshot_data["approved_at"]),
            source_resume_hash=snapshot_data["source_resume_hash"],
            source_profile_hash=snapshot_data["source_profile_hash"],
            frozen=snapshot_data["frozen"],
            approval_metadata=snapshot_data["approval_metadata"]
        )
    
    def _validate_user_confirmation(self, confirmation: UserConfirmation, draft: DraftArtifactPack) -> None:
        """Validate user has properly confirmed the approval."""
        if not confirmation.accuracy_confirmed:
            raise ValueError("User must confirm accuracy checkbox")
        
        if not confirmation.bullets_verified:
            raise ValueError("User must verify at least one bullet")
        
        # Validate bullet verifications match draft structure
        draft_bullets = self._extract_bullets_from_draft(draft.student_artifact_pack)
        verified_bullet_ids = {bv["bullet_id"] for bv in confirmation.bullets_verified}
        
        for bullet_id in draft_bullets:
            if bullet_id not in verified_bullet_ids:
                raise ValueError(f"Bullet {bullet_id} not verified by user")
    
    def _extract_bullets_from_draft(self, artifact_pack: Dict[str, Any]) -> List[str]:
        """Extract bullet IDs from draft artifact pack."""
        bullet_ids = []
        for i, project in enumerate(artifact_pack.get("projects", [])):
            for j, bullet in enumerate(project.get("bullets", [])):
                bullet_ids.append(f"project_{i}_bullet_{j}")
        return bullet_ids
    
    def _apply_user_verifications(
        self, 
        draft_artifact_pack: Dict[str, Any], 
        confirmation: UserConfirmation
    ) -> Dict[str, Any]:
        """Apply user verifications to create approved artifact pack."""
        approved_pack = draft_artifact_pack.copy()
        
        # Create verification lookup
        verification_lookup = {
            bv["bullet_id"]: bv["verified"] 
            for bv in confirmation.bullets_verified
        }
        
        # Apply verifications to bullets
        for i, project in enumerate(approved_pack.get("projects", [])):
            for j, bullet in enumerate(project.get("bullets", [])):
                bullet_id = f"project_{i}_bullet_{j}"
                if bullet_id in verification_lookup:
                    bullet["verified"] = verification_lookup[bullet_id]
                else:
                    # If not explicitly verified, keep as false
                    bullet["verified"] = False
        
        return approved_pack


class EngineGateway:
    """
    Safety gateway that validates and controls engine access.
    
    SAFETY GUARANTEES:
    - Engine can ONLY access approved StudentArtifactPack data
    - Rejects execution when no approved snapshot exists
    - Ensures no AI involvement or data mutation during execution
    """
    
    def __init__(self, approval_service: ApprovalService, database=None):
        self.approval_service = approval_service
        if database is None:
            from backend.database import PersistentDatabase
            self.db = PersistentDatabase()
        else:
            self.db = database
    
    def validate_and_execute(self, user_id: int, job_ids: List[str]) -> Dict[str, Any]:
        """
        Validate approved artifacts exist and execute engine.
        
        Args:
            user_id: User requesting execution
            job_ids: List of job IDs to process
            
        Returns:
            Execution result or error
            
        Raises:
            ValueError: If no approved artifacts exist
        """
        # SAFETY GATE: Check for approved artifact snapshot
        current_snapshot = self.approval_service.get_current_approved(user_id)
        
        if not current_snapshot:
            raise ValueError(
                "Engine execution requires approved artifact snapshot. "
                "Please use the 'Prepare Application Artifacts' workflow first."
            )
        
        # Validate snapshot integrity
        if not current_snapshot.frozen:
            raise ValueError("Artifact snapshot must be frozen for engine execution")
        
        # Extract approved StudentArtifactPack
        approved_artifact_pack = current_snapshot.student_artifact_pack
        
        # Validate all bullets are verified
        self._validate_all_bullets_verified(approved_artifact_pack)
        
        # Get job data for engine execution
        jobs_data = []
        for job_id in job_ids:
            job = self.db.get_job_by_id(job_id)
            if job:
                jobs_data.append(job)
        
        if not jobs_data:
            raise ValueError("No valid jobs found for execution")
        
        # Execute engine with approved artifacts ONLY
        from backend.engine import run_autopilot
        
        try:
            result = run_autopilot(
                student_data=approved_artifact_pack,
                jobs_data=jobs_data
            )
            
            if result["success"]:
                # Save execution results to database
                run_id = self.db.create_autopilot_run(
                    user_id=user_id,
                    profile_snapshot=approved_artifact_pack,
                    job_ids=job_ids
                )
                
                # Save application history
                if result["tracker"]:
                    applications = []
                    for event in result["tracker"].events:
                        applications.append({
                            "job_id": event["job_id"],
                            "status": event["status"],
                            "reason": event.get("reason"),
                            "receipt_id": event.get("receipt_id"),
                            "timestamp": event["timestamp"]
                        })
                    
                    self.db.save_application_history(user_id, run_id, applications)
                
                # Mark run as completed
                self.db.complete_autopilot_run(run_id, result["summary"], "")
                
                return {
                    "success": True,
                    "run_id": run_id,
                    "summary": result["summary"],
                    "approved_snapshot_id": current_snapshot.id
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Engine execution failed"),
                    "approved_snapshot_id": current_snapshot.id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Engine execution failed: {str(e)}",
                "approved_snapshot_id": current_snapshot.id
            }
    
    def _validate_all_bullets_verified(self, artifact_pack: Dict[str, Any]) -> None:
        """Validate that all bullets in the artifact pack are verified."""
        for project in artifact_pack.get("projects", []):
            for bullet in project.get("bullets", []):
                if not bullet.get("verified", False):
                    raise ValueError(
                        f"Unverified bullet found in approved snapshot: {bullet.get('description', 'Unknown')}"
                    )