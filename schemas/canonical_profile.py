"""
Canonical Student Profile Schema and Factory Functions
SINGLE SOURCE OF TRUTH for profile structure
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid


def create_canonical_profile_template(student_id: str) -> Dict[str, Any]:
    """
    Create a canonical profile template with all required sections.
    Use this as the base for resume extraction.
    """
    return {
        "student_id": student_id,
        "education": [],
        "projects": [],
        "internships": [],
        "skills": [],
        "links": {
            "github": None,
            "linkedin": None,
            "portfolio": None
        },
        "constraints": {
            "preferred_roles": [],
            "preferred_locations": [],
            "remote_allowed": True,
            "visa_required": False,
            "start_date": None,
            "blocked_companies": [],
            "min_match_score": 70,
            "max_applications_per_day": 10
        },
        "extraction_meta": {
            "education_found": False,
            "projects_found": False,
            "internships_found": False,
            "skills_found": False
        },
        "provenance": {
            "education": "not_extracted",
            "projects": "not_extracted",
            "internships": "not_extracted",
            "skills": "not_extracted"
        },
        "last_validated_at": datetime.utcnow().isoformat()
    }


def create_education_entry(institution: str, degree: str, field: str, 
                          start_year: int, end_year: int) -> Dict[str, Any]:
    """Create a structured education entry."""
    return {
        "institution": institution,
        "degree": degree,
        "field": field,
        "start_year": start_year,
        "end_year": end_year
    }


def create_project_entry(title: str, description: str, skills_used: List[str], 
                        proof_link: Optional[str] = None) -> Dict[str, Any]:
    """Create a structured project entry."""
    return {
        "project_id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "skills_used": skills_used,
        "proof_link": proof_link
    }


def create_internship_entry(company: str, role: str, start_date: str, 
                           end_date: Optional[str], responsibilities: List[str]) -> Dict[str, Any]:
    """Create a structured internship entry."""
    return {
        "company": company,
        "role": role,
        "start_date": start_date,  # YYYY-MM format
        "end_date": end_date,      # YYYY-MM format or null
        "responsibilities": responsibilities
    }


def mark_section_extracted(profile: Dict[str, Any], section: str, found: bool, 
                          provenance: str = "resume") -> None:
    """Mark a section as extracted and update metadata."""
    profile["extraction_meta"][f"{section}_found"] = found
    profile["provenance"][section] = provenance if found else "not_found_in_resume"
    profile["last_validated_at"] = datetime.utcnow().isoformat()


# Example of a complete canonical profile
EXAMPLE_CANONICAL_PROFILE = {
    "student_id": "student_12345",
    "education": [
        {
            "institution": "University of California, Berkeley",
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "start_year": 2021,
            "end_year": 2025
        }
    ],
    "projects": [
        {
            "project_id": "proj_001",
            "title": "Job Application Automation System",
            "description": "Built an autonomous job application system using Python, Flask, and ML ranking algorithms",
            "skills_used": ["python", "flask", "machine learning", "sqlite"],
            "proof_link": "https://github.com/username/job-automation"
        }
    ],
    "internships": [
        {
            "company": "Google",
            "role": "Software Engineering Intern",
            "start_date": "2024-06",
            "end_date": "2024-08",
            "responsibilities": [
                "Developed microservices using Go and Kubernetes",
                "Improved system performance by 25%"
            ]
        }
    ],
    "skills": ["python", "javascript", "react", "sql", "machine learning", "docker"],
    "links": {
        "github": "https://github.com/username",
        "linkedin": "https://linkedin.com/in/username",
        "portfolio": "https://username.dev"
    },
    "constraints": {
        "preferred_roles": ["Software Engineer", "ML Engineer", "Backend Developer"],
        "preferred_locations": ["San Francisco", "New York", "Remote"],
        "remote_allowed": True,
        "visa_required": False,
        "start_date": "2025-06",
        "blocked_companies": ["Meta"],
        "min_match_score": 75,
        "max_applications_per_day": 15
    },
    "extraction_meta": {
        "education_found": True,
        "projects_found": True,
        "internships_found": True,
        "skills_found": True
    },
    "provenance": {
        "education": "resume",
        "projects": "resume",
        "internships": "resume",
        "skills": "resume+manual"
    },
    "last_validated_at": "2025-02-01T10:30:00Z"
}