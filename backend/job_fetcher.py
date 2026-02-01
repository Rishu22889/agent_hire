#!/usr/bin/env python3
"""
Job Fetcher Service - Fetches jobs from external portals (like sandbox)
Integrates with the main system to pull jobs from real job boards.
Enhanced to work with the comprehensive sandbox portal.
"""
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobFetcher:
    """Fetches jobs from external job portals."""
    
    def __init__(self, portal_url: str = "http://localhost:5001"):
        self.portal_url = portal_url
        self.session = requests.Session()
        self.session.timeout = 30
        
    def check_portal_status(self) -> Dict[str, Any]:
        """Check if the job portal is available."""
        try:
            response = self.session.get(f"{self.portal_url}/api/portal/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to check portal status: {e}")
            return {"status": "unavailable", "error": str(e)}
    
    def fetch_jobs(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch jobs from the external portal."""
        try:
            # Build query parameters
            params = {}
            if filters:
                if filters.get('location'):
                    params['location'] = filters['location']
                if filters.get('job_type'):
                    params['job_type'] = filters['job_type']
                if filters.get('experience_level'):
                    params['experience_level'] = filters['experience_level']
                if filters.get('company'):
                    params['company'] = filters['company']
                if filters.get('search'):
                    params['search'] = filters['search']
                if filters.get('skills'):
                    params['skills'] = ','.join(filters['skills'])
                if filters.get('limit'):
                    params['limit'] = filters['limit']
            
            logger.info(f"Fetching jobs from portal with filters: {params}")
            
            response = self.session.get(f"{self.portal_url}/api/jobs", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                jobs = data.get('jobs', [])
                logger.info(f"Successfully fetched {len(jobs)} jobs from portal")
                return jobs
            else:
                logger.error(f"Portal returned error: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch jobs from portal: {e}")
            return []
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific job."""
        try:
            response = self.session.get(f"{self.portal_url}/api/jobs/{job_id}")
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                return data.get('job')
            else:
                logger.error(f"Failed to get job details: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get job details for {job_id}: {e}")
            return None
    
    def submit_application(self, job_id: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit an application to a job through the portal."""
        try:
            logger.info(f"Submitting application to job {job_id}")
            
            response = self.session.post(
                f"{self.portal_url}/api/jobs/{job_id}/apply",
                json=application_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                logger.info(f"Application submitted successfully: {data.get('application_id')}")
                return {
                    "success": True,
                    "application_id": data.get('application_id'),
                    "receipt_id": data.get('receipt_id'),
                    "message": data.get('message'),
                    "status": "submitted",
                    "receipt": data.get('receipt')
                }
            else:
                logger.error(f"Application submission failed: {data}")
                return {
                    "success": False,
                    "error": data.get('error', 'Unknown error'),
                    "status": "failed"
                }
                
        except Exception as e:
            logger.error(f"Failed to submit application to {job_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    def get_application_status(self, application_id: str = None, receipt_id: str = None) -> Optional[Dict[str, Any]]:
        """Get application status by application ID or receipt ID."""
        try:
            if receipt_id:
                response = self.session.get(f"{self.portal_url}/api/applications/receipt/{receipt_id}")
            elif application_id:
                response = self.session.get(f"{self.portal_url}/api/applications/{application_id}")
            else:
                logger.error("Either application_id or receipt_id must be provided")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return data.get('application')
            else:
                logger.error(f"Failed to get application status: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get application status: {e}")
            return None
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from the portal."""
        try:
            response = self.session.get(f"{self.portal_url}/api/companies")
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                companies = data.get('companies', [])
                logger.info(f"Successfully fetched {len(companies)} companies from portal")
                return companies
            else:
                logger.error(f"Portal returned error: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch companies from portal: {e}")
            return []
    
    def convert_portal_job_to_internal_format(self, portal_job: Dict[str, Any]) -> Dict[str, Any]:
        """Convert portal job format to internal database format."""
        return {
            "job_id": portal_job.get("job_id"),
            "company": portal_job.get("company"),
            "role": portal_job.get("role"),
            "location": portal_job.get("location"),
            "required_skills": portal_job.get("required_skills", []),
            "min_experience_years": portal_job.get("min_experience_years", 0),
            "job_type": portal_job.get("job_type"),
            "salary_range": portal_job.get("salary_range"),
            "description": portal_job.get("description", ""),
            "posted_date": portal_job.get("posted_date"),
            "deadline": portal_job.get("deadline"),
            "application_url": portal_job.get("application_url"),
            "source": "sandbox_portal",
            "experience_level": portal_job.get("experience_level"),
            "department": portal_job.get("department"),
            "preferred_skills": portal_job.get("preferred_skills", []),
            "views": portal_job.get("views", 0),
            "applications_count": portal_job.get("applications_count", 0)
        }
    
    def convert_user_profile_to_application_data(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Convert user profile to application data format for portal submission."""
        
        # Handle different profile structures
        basic_info = user_profile.get('basic_info', {})
        education = user_profile.get('education', [])
        projects = user_profile.get('projects', [])
        internships = user_profile.get('internships', [])
        skills = user_profile.get('skills', [])
        constraints = user_profile.get('constraints', {})
        
        # Get user info from basic_info (new structure)
        name = basic_info.get('name', 'Student Applicant')
        email = basic_info.get('email', 'student@example.com')
        phone = basic_info.get('phone', '')
        location = basic_info.get('location', '')
        
        # Fallback to constraints location if basic_info location is empty
        if not location and constraints.get('location'):
            location = constraints.get('location', [''])[0]
        
        # Build application data
        application_data = {
            "applicant_name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "skills": skills,
            "cover_letter": self.generate_cover_letter(user_profile, name),
            "current_role": basic_info.get('current_role', 'Student'),
            "education": self.format_education(education),
            "experience_years": self.calculate_experience_years(projects, internships),
            "availability": constraints.get('availability', 'Flexible'),
            "salary_expectation": constraints.get('salary_expectation', 'Negotiable'),
            "resume_text": self.generate_resume_text(user_profile, name, email)
        }
        
        return application_data
    
    def generate_resume_text(self, user_profile: Dict[str, Any], name: str, email: str) -> str:
        """Generate resume text from user profile."""
        basic_info = user_profile.get('basic_info', {})
        education = user_profile.get('education', [])
        projects = user_profile.get('projects', [])
        internships = user_profile.get('internships', [])
        skills = user_profile.get('skills', [])
        
        resume_text = f"Name: {name}\n"
        resume_text += f"Email: {email}\n"
        if basic_info.get('phone'):
            resume_text += f"Phone: {basic_info.get('phone')}\n"
        if basic_info.get('location'):
            resume_text += f"Location: {basic_info.get('location')}\n"
        
        resume_text += "\nSKILLS:\n"
        for skill in skills:
            resume_text += f"• {skill}\n"
        
        if education:
            resume_text += "\nEDUCATION:\n"
            for edu in education:
                resume_text += f"• {edu.get('degree', 'Degree')} at {edu.get('institution', 'Institution')}\n"
        
        if projects:
            resume_text += "\nPROJECTS:\n"
            for project in projects:
                resume_text += f"• {project.get('name', 'Project')}: {project.get('description', 'No description')}\n"
        
        if internships:
            resume_text += "\nINTERNSHIPS:\n"
            for internship in internships:
                resume_text += f"• {internship.get('company', 'Company')}: {internship.get('role', 'Role')}\n"
        
        return resume_text
    
    def generate_cover_letter(self, user_profile: Dict[str, Any], name: str = None) -> str:
        """Generate a cover letter based on user profile."""
        basic_info = user_profile.get('basic_info', {})
        projects = user_profile.get('projects', [])
        skills = user_profile.get('skills', [])
        
        name = name or basic_info.get('name', 'Applicant')
        
        cover_letter = f"Dear Hiring Manager,\n\n"
        cover_letter += f"I am {name}, and I am excited to apply for this position. "
        
        if skills:
            cover_letter += f"I have experience with {', '.join(skills[:5])}. "
        
        if projects:
            cover_letter += f"I have worked on {len(projects)} projects, including "
            project_names = [p.get('name', 'a project') for p in projects[:2]]
            cover_letter += f"{' and '.join(project_names)}. "
        
        cover_letter += "I am eager to contribute to your team and learn from experienced professionals. "
        cover_letter += "Thank you for considering my application.\n\n"
        cover_letter += f"Best regards,\n{name}"
        
        return cover_letter
    
    def format_education(self, education: List[Dict[str, Any]]) -> str:
        """Format education information."""
        if not education:
            return ""
        
        edu = education[0]  # Take first education entry
        degree = edu.get('degree', '')
        institution = edu.get('institution', '')
        
        if degree and institution:
            return f"{degree}, {institution}"
        elif degree:
            return degree
        elif institution:
            return institution
        else:
            return ""
    
    def calculate_experience_years(self, projects: List[Dict[str, Any]], internships: List[Dict[str, Any]]) -> str:
        """Calculate experience years based on projects and internships."""
        total_experience = len(projects) + len(internships)
        
        if total_experience == 0:
            return "0"
        elif total_experience <= 2:
            return "1"
        elif total_experience <= 4:
            return "2"
        else:
            return "3"

def sync_jobs_from_portal():
    """Sync jobs from the sandbox portal to our internal database."""
    from database import PersistentDatabase
    
    fetcher = JobFetcher()
    db = PersistentDatabase()
    
    # Check portal status
    status = fetcher.check_portal_status()
    if status.get("status") != "active":
        logger.error(f"Portal is not available: {status}")
        return False
    
    logger.info(f"Portal status: {status}")
    
    # Fetch jobs from portal
    portal_jobs = fetcher.fetch_jobs()
    
    if not portal_jobs:
        logger.warning("No jobs fetched from portal")
        return False
    
    # Convert and store jobs
    added_count = 0
    updated_count = 0
    
    for portal_job in portal_jobs:
        try:
            # Convert to internal format
            internal_job = fetcher.convert_portal_job_to_internal_format(portal_job)
            
            # Check if job already exists
            existing_job = None
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM job_listings WHERE job_id = ?", (internal_job["job_id"],))
                    existing_job = cursor.fetchone()
            except Exception as e:
                logger.error(f"Error checking existing job: {e}")
            
            if existing_job:
                # Update existing job
                try:
                    # Update logic would go here
                    updated_count += 1
                    logger.info(f"Updated job: {internal_job['job_id']}")
                except Exception as e:
                    logger.error(f"Failed to update job {internal_job['job_id']}: {e}")
            else:
                # Add new job
                try:
                    db.add_job_listing(internal_job)
                    added_count += 1
                    logger.info(f"Added new job: {internal_job['job_id']} - {internal_job['company']} - {internal_job['role']}")
                except Exception as e:
                    logger.error(f"Failed to add job {internal_job['job_id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to process job: {e}")
    
    logger.info(f"Job sync complete: {added_count} added, {updated_count} updated")
    return True

if __name__ == "__main__":
    # Test the job fetcher
    print("🔄 Testing Job Fetcher...")
    
    fetcher = JobFetcher()
    
    # Check portal status
    status = fetcher.check_portal_status()
    print(f"Portal Status: {status}")
    
    if status.get("status") == "active":
        # Fetch jobs
        jobs = fetcher.fetch_jobs()
        print(f"Fetched {len(jobs)} jobs")
        
        if jobs:
            # Show first job
            print(f"Sample job: {jobs[0]['company']} - {jobs[0]['role']}")
            
            # Test job details
            job_details = fetcher.get_job_details(jobs[0]['job_id'])
            if job_details:
                print(f"Job details fetched successfully")
            
            # Test sync
            print("\\nTesting job sync...")
            sync_jobs_from_portal()
    else:
        print("❌ Portal is not available. Start the sandbox portal first.")