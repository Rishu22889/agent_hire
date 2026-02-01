"""
Status indication functions for the artifact approval workflow.

These functions provide clear status indicators for draft vs approved artifacts,
ensuring the approval workflow is transparent to users.
"""
from typing import Dict, Any, Optional
from backend.models import DraftArtifactPack, ArtifactSnapshot


def get_artifact_status_display(
    draft_artifact: Optional[DraftArtifactPack] = None,
    approved_snapshot: Optional[ArtifactSnapshot] = None
) -> Dict[str, Any]:
    """
    Get display status for artifacts.
    
    Args:
        draft_artifact: Current draft artifact (if any)
        approved_snapshot: Current approved snapshot (if any)
        
    Returns:
        Status display information
    """
    if approved_snapshot:
        return {
            "status": "APPROVED",
            "status_class": "success",
            "status_message": "✅ Artifacts approved - Engine execution enabled",
            "action_required": None,
            "approved_at": approved_snapshot.approved_at.isoformat(),
            "snapshot_id": approved_snapshot.id
        }
    elif draft_artifact:
        return {
            "status": "DRAFT",
            "status_class": "warning", 
            "status_message": "⚠️ Draft artifacts - NOT APPROVED",
            "action_required": "Please review and approve artifacts before engine execution",
            "created_at": draft_artifact.created_at.isoformat(),
            "draft_status": draft_artifact.status
        }
    else:
        return {
            "status": "NONE",
            "status_class": "info",
            "status_message": "ℹ️ No artifacts generated",
            "action_required": "Please generate artifacts from your profile first",
            "created_at": None,
            "draft_status": None
        }


def get_draft_artifact_indicators(draft_artifact: DraftArtifactPack) -> Dict[str, Any]:
    """
    Get specific indicators for draft artifacts.
    
    Args:
        draft_artifact: Draft artifact to analyze
        
    Returns:
        Draft-specific indicators
    """
    student_pack = draft_artifact.student_artifact_pack
    
    # Count unverified bullets
    total_bullets = 0
    unverified_bullets = 0
    
    for project in student_pack.get("projects", []):
        for bullet in project.get("bullets", []):
            total_bullets += 1
            if not bullet.get("verified", False):
                unverified_bullets += 1
    
    return {
        "is_draft": True,
        "status_badge": "NOT APPROVED",
        "status_color": "orange",
        "total_bullets": total_bullets,
        "unverified_bullets": unverified_bullets,
        "verification_progress": f"{total_bullets - unverified_bullets}/{total_bullets} verified",
        "ready_for_approval": unverified_bullets == 0,
        "warning_message": "⚠️ This is a DRAFT. All bullets must be verified before approval."
    }


def get_approved_artifact_indicators(approved_snapshot: ArtifactSnapshot) -> Dict[str, Any]:
    """
    Get specific indicators for approved artifacts.
    
    Args:
        approved_snapshot: Approved snapshot to analyze
        
    Returns:
        Approval-specific indicators
    """
    student_pack = approved_snapshot.student_artifact_pack
    
    # Count verified bullets
    total_bullets = 0
    verified_bullets = 0
    
    for project in student_pack.get("projects", []):
        for bullet in project.get("bullets", []):
            total_bullets += 1
            if bullet.get("verified", False):
                verified_bullets += 1
    
    return {
        "is_approved": True,
        "status_badge": "APPROVED",
        "status_color": "green",
        "total_bullets": total_bullets,
        "verified_bullets": verified_bullets,
        "frozen": approved_snapshot.frozen,
        "approved_at": approved_snapshot.approved_at.isoformat(),
        "success_message": "✅ Artifacts approved and frozen. Engine execution enabled.",
        "integrity_hash": approved_snapshot.generate_integrity_hash()
    }


def get_engine_execution_status(
    approved_snapshot: Optional[ArtifactSnapshot] = None
) -> Dict[str, Any]:
    """
    Get engine execution status based on artifact approval state.
    
    Args:
        approved_snapshot: Current approved snapshot (if any)
        
    Returns:
        Engine execution status information
    """
    if approved_snapshot:
        return {
            "execution_enabled": True,
            "status_message": "✅ Engine execution enabled",
            "status_class": "success",
            "button_text": "Run Autopilot",
            "button_enabled": True,
            "requirement_met": "Approved artifacts available"
        }
    else:
        return {
            "execution_enabled": False,
            "status_message": "❌ Engine execution disabled",
            "status_class": "danger",
            "button_text": "Approve Artifacts First",
            "button_enabled": False,
            "requirement_met": "No approved artifacts - please generate and approve first"
        }


def format_approval_workflow_status(
    user_profile_modified: Optional[str] = None,
    draft_created: Optional[str] = None,
    approved_at: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format the complete approval workflow status.
    
    Args:
        user_profile_modified: When user profile was last modified
        draft_created: When draft was created
        approved_at: When artifacts were approved
        
    Returns:
        Complete workflow status
    """
    workflow_steps = [
        {
            "step": 1,
            "name": "Edit Profile",
            "status": "completed" if user_profile_modified else "pending",
            "timestamp": user_profile_modified,
            "description": "Create and edit your user profile"
        },
        {
            "step": 2,
            "name": "Generate Draft",
            "status": "completed" if draft_created else "pending",
            "timestamp": draft_created,
            "description": "Generate draft artifacts from profile"
        },
        {
            "step": 3,
            "name": "Review & Approve",
            "status": "completed" if approved_at else "pending",
            "timestamp": approved_at,
            "description": "Review and approve artifacts for engine use"
        },
        {
            "step": 4,
            "name": "Engine Execution",
            "status": "enabled" if approved_at else "disabled",
            "timestamp": None,
            "description": "Run autopilot with approved artifacts"
        }
    ]
    
    # Determine current step
    if approved_at:
        current_step = 4
        overall_status = "ready_for_execution"
    elif draft_created:
        current_step = 3
        overall_status = "awaiting_approval"
    elif user_profile_modified:
        current_step = 2
        overall_status = "awaiting_draft_generation"
    else:
        current_step = 1
        overall_status = "awaiting_profile"
    
    return {
        "workflow_steps": workflow_steps,
        "current_step": current_step,
        "overall_status": overall_status,
        "progress_percentage": (current_step - 1) * 25,
        "next_action": workflow_steps[current_step - 1]["description"] if current_step <= 4 else "Execute autopilot"
    }