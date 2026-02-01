from typing import Dict, Any, Optional, Tuple, List
from schemas.student_schema import StudentArtifactPack, Bullet
from schemas.job_schema import JobListing

# Dummy Answer Library (for use if additional question/answer logic required)
# For this implementation, no answers are produced except from officially defined library (which is absent)
ANSWER_LIBRARY = {}

def generate_application_content(
    student: StudentArtifactPack,
    job: JobListing
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Generates application content for a student applying to a job.

    Args:
        student (StudentArtifactPack): The student's artifact pack.
        job (JobListing): The target job listing.

    Returns:
        (Dict or None, skip_reason or None): Returns a dict with keys:
            - selected_bullets: List[Bullet]
            - cover_paragraph: str
            - answers: dict (empty unless otherwise defined)
        Or None and a skip reason if not eligible.
    """
    relevant_verified_bullets: List[Bullet] = []
    job_skill_set = set(job.required_skills)

    for project in getattr(student, "projects", []):
        for bullet in getattr(project, "bullets", []):
            # Must use only verified bullets (schema already verifies this on instantiation)
            bullet_skills_set = set(bullet.skills)
            if bullet_skills_set & job_skill_set:
                relevant_verified_bullets.append(bullet)

    if not relevant_verified_bullets:
        return None, "NO_RELEVANT_VERIFIED_BULLETS"

    bullet_descriptions = [b.description for b in relevant_verified_bullets]
    bullet_summary = ", ".join(bullet_descriptions)
    cover_paragraph = (
        f"I am applying for the {job.role} position. My background includes {bullet_summary}."
    )

    # All answers must come explicitly from the library (library is read-only, here empty)
    answers = {}

    relevant_verified_bullets = relevant_verified_bullets[:3]

    result = {
        "selected_bullets": relevant_verified_bullets,
        "cover_paragraph": cover_paragraph,
        "answers": answers,
    }
    return result, None