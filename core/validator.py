from typing import Tuple
from schemas.student_schema import StudentArtifactPack
from schemas.job_schema import JobListing

def validate_job_for_scoring(
    student: StudentArtifactPack,
    job: JobListing,
    apps_today: int
) -> Tuple[bool, str]:
    """
    Determines whether a job should be considered for scoring or skipped.

    Args:
        student (StudentArtifactPack): The student's artifact record.
        job (JobListing): The job listing being considered.
        apps_today (int): The number of applications made by the student today.

    Returns:
        (allowed: bool, reason: str): Whether the job is allowed and reason for skip if not.
    """

    constraints = student.constraints
    skill_vocab = set(student.skill_vocab)

    if not student.constraints:
        return (False, "Student constraints not defined; refusing to score job.")

    # 1. Blocked company check
    if constraints and job.company in getattr(constraints, "blocked_companies", []):
        return (False, f"Company '{job.company}' is in the student's blocked_companies list.")

    # 2. Applications per day limit check
    if constraints and hasattr(constraints, "max_apps_per_day"):
        if apps_today >= constraints.max_apps_per_day:
            return (False, "Student has exceeded the maximum allowed applications per day.")

    # 3. Unknown required skill check
    unknown_skills = [s for s in job.required_skills if s not in skill_vocab]
    if unknown_skills:
        return (
            False,
            f"Job requires skill(s) {unknown_skills} that are not in the student's skill vocabulary."
        )

    # 4. Internship requirement check
    if job.min_experience_years > 0:
        # No internships field is defined in the schema; experience claims are not permitted.
        return (False, "Job requires prior experience, but no internships field is defined in the student profile")

    # If all checks pass
    return (True, "Job passes all hard validation gates.")