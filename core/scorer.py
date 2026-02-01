from typing import Dict, Any
from schemas.student_schema import StudentArtifactPack
from schemas.job_schema import JobListing

def score_job_match(
    student: StudentArtifactPack,
    job: JobListing
) -> Dict[str, Any]:
    """
    Computes a match score between a student and a job listing.

    Scoring breakdown:
      - skill_overlap:   50%
      - experience_fit:  30%
      - constraint_match: 20% (always 1.0, handled outside this function)

    Args:
        student (StudentArtifactPack): The student.
        job (JobListing): The job listing.

    Returns:
        Dict[str, Any]: {
            "score": float,              # overall match score 0.0 - 1.0
            "explanation": {
                "skill_overlap": float,   # component [0.0-1.0]
                "experience_fit": float,  # component [0.0-1.0]
                "constraint_match": float # always 1.0
            }
        }
    """
    # Skill overlap
    required_skills = set(job.required_skills)
    student_skills = set(student.skill_vocab)
    if not required_skills:
        skill_overlap = 1.0
    else:
        matched = len(required_skills & student_skills)
        skill_overlap = matched / len(required_skills) if required_skills else 1.0

    # Experience fit
    experience_fit = 1.0 if job.min_experience_years == 0 else 0.0

    # Constraint match (always 1.0 here; gating logic handled elsewhere)
    constraint_match = 1.0

    score = (
        0.5 * skill_overlap +
        0.3 * experience_fit +
        0.2 * constraint_match
    )

    score = max(0.0, min(1.0, score))

    return {
        "score": score,
        "explanation": {
            "skill_overlap": skill_overlap,
            "experience_fit": experience_fit,
            "constraint_match": constraint_match,
            "final_score": score
        }
    }