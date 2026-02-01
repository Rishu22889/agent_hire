"""
Reusable autopilot engine wrapper.
Preserves all original logic from main.py while making it callable as a function.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.tracker import ApplicationTracker
from sandbox.portal import SandboxJobPortal
from core.scorer import score_job_match
from core.generator import generate_application_content
from schemas.student_schema import StudentArtifactPack
from schemas.job_schema import JobListing
from core.validator import validate_job_for_scoring


def load_json(path):
    """Load JSON data from file path."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_autopilot(
    student_data: Dict[str, Any],
    jobs_data: List[Dict[str, Any]],
    tracker: Optional[ApplicationTracker] = None
) -> Dict[str, Any]:
    """
    Run the autonomous job application engine.
    
    Args:
        student_data: Raw student profile data (will be validated against schema)
        jobs_data: List of raw job listing data (will be validated against schema)
        tracker: Optional existing tracker, creates new one if None
    
    Returns:
        Dict containing:
        - summary: Dict with counts (queued, skipped, submitted, failed, retried)
        - tracker: ApplicationTracker instance with all logged events
        - success: bool indicating if execution completed
        - error: Optional error message if validation failed
    """
    
    # Validate schemas
    try:
        student = StudentArtifactPack(**student_data)
    except Exception as e:
        return {
            "success": False,
            "error": f"Student profile schema validation failed: {e}",
            "summary": {},
            "tracker": None
        }

    jobs = []
    for idx, j in enumerate(jobs_data):
        try:
            jobs.append(JobListing(**j))
        except Exception as e:
            return {
                "success": False,
                "error": f"Job entry #{idx+1} schema validation failed: {e}",
                "summary": {},
                "tracker": None
            }

    # Initialize tracker and portal
    if tracker is None:
        tracker = ApplicationTracker()
    portal = SandboxJobPortal()

    # Summary counts
    queued, skipped, submitted, failed, retried = 0, 0, 0, 0, 0
    apps_today = 0

    # Process each job (preserving exact original logic)
    for job in jobs:
        job_id = job.job_id
        # Track status "queued"
        tracker.track(job_id=job_id, status="queued")
        queued += 1

        # Validate job for scoring
        ok, not_allowed_reason = validate_job_for_scoring(student, job, apps_today)
        if not ok:
            tracker.track(job_id=job_id, status="skipped", reason=not_allowed_reason)
            skipped += 1
            continue

        # Score job
        score_result = score_job_match(student, job)
        score = score_result["score"]

        min_score = student.constraints.min_match_score

        if score < min_score:
            reason = f"Score {score:.2f} < required {min_score:.2f}"
            tracker.track(job_id=job_id, status="skipped", reason=reason)
            skipped += 1
            continue

        # Generate application content
        app_content, skip_reason = generate_application_content(student, job)
        if app_content is None:
            tracker.track(job_id=job_id, status="skipped", reason=skip_reason)
            skipped += 1
            continue

        # Compose application dict for submission
        application = {
            "job_id": job_id,
            "student_id": student.source_resume_hash,
            "content": app_content,
        }

        # Submit to sandbox portal (with retry logic)
        try:
            submission_result = portal.submit_application(application)
            tracker.track(
                job_id=job_id,
                status="submitted",
                receipt_id=submission_result.get("receipt_id")
            )
            submitted += 1
        except Exception as e1:
            try:
                submission_result = portal.submit_application(application)
                tracker.track(
                    job_id=job_id,
                    status="retried",
                    receipt_id=submission_result.get("receipt_id")
                )
                retried += 1
            except Exception as e2:
                tracker.track(
                    job_id=job_id,
                    status="failed",
                    reason=f"Submission failed twice: {e2}"
                )
                failed += 1
        apps_today += 1

    summary = {
        "queued": queued,
        "skipped": skipped,
        "submitted": submitted,
        "retried": retried,
        "failed": failed
    }

    return {
        "success": True,
        "error": None,
        "summary": summary,
        "tracker": tracker
    }


def run_autopilot_from_files(
    student_path: str = "data/student_profile.json",
    jobs_path: str = "data/jobs.json"
) -> Dict[str, Any]:
    """
    Run autopilot using file paths (backward compatibility with original main.py).
    
    Args:
        student_path: Path to student profile JSON
        jobs_path: Path to jobs JSON
    
    Returns:
        Same as run_autopilot()
    """
    try:
        student_data = load_json(student_path)
        jobs_data = load_json(jobs_path)
        return run_autopilot(student_data, jobs_data)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load files: {e}",
            "summary": {},
            "tracker": None
        }