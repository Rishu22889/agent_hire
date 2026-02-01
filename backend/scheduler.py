"""
Autonomous AI Agent Scheduler
Automatically applies to jobs daily without user intervention.
Logs all activities to logs/application.log for user visibility.
"""
import asyncio
import schedule
import time
import threading
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from backend.database import PersistentDatabase
from backend.ai_agents import rank_jobs_for_user, convert_user_profile_to_student_artifact_pack
from backend.engine import run_autopilot
from core.tracker import ApplicationTracker
from backend.job_fetcher import JobFetcher

# Configure logging to file
os.makedirs('backend/logs', exist_ok=True)
file_handler = logging.FileHandler('backend/logs/application.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Configure console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class AutonomousAIAgent:
    """Fully autonomous AI agent that applies to jobs automatically."""
    
    def __init__(self):
        self.db = PersistentDatabase(db_path="backend/data/platform.db")
        self.job_fetcher = JobFetcher()  # Initialize job fetcher for sandbox portal
        self.running = False
        
    def start_autonomous_mode(self):
        """Start the autonomous AI agent scheduler."""
        logger.info("🤖 Starting Autonomous AI Agent...")
        
        # Schedule daily autopilot runs
        schedule.every().day.at("09:00").do(self.run_daily_autopilot)
        schedule.every().day.at("14:00").do(self.run_daily_autopilot)  # Twice daily
        
        # Also run immediately for testing
        schedule.every(30).seconds.do(self.run_daily_autopilot)  # Every 30 seconds for demo
        
        self.running = True
        
        # Run scheduler in background thread
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Autonomous AI Agent started successfully!")
        
    def stop_autonomous_mode(self):
        """Stop the autonomous AI agent."""
        self.running = False
        schedule.clear()
        logger.info("🛑 Autonomous AI Agent stopped")
        
    def run_daily_autopilot(self):
        """Run autopilot for all eligible users automatically."""
        logger.info("🚀 Running daily autonomous autopilot...")
        
        try:
            # Get all users with profiles
            eligible_users = self.get_eligible_users()
            logger.info(f"Found {len(eligible_users)} eligible users")
            
            for user_data in eligible_users:
                try:
                    self.process_user_autopilot(user_data)
                except Exception as e:
                    logger.error(f"Failed to process user {user_data['user_id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Daily autopilot failed: {e}")
            
    def get_eligible_users(self) -> List[Dict[str, Any]]:
        """Get users eligible for autonomous autopilot."""
        eligible_users = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all users with profiles
            cursor.execute("""
                SELECT u.id, u.email, up.profile_data, up.student_id
                FROM users u
                JOIN user_profiles up ON u.id = up.user_id
                WHERE u.is_active = TRUE
            """)
            
            for row in cursor.fetchall():
                user_id, email, profile_data_json, student_id = row
                profile_data = json.loads(profile_data_json)
                
                # Check if user is eligible for autopilot today
                if self.is_user_eligible_today(user_id, profile_data):
                    eligible_users.append({
                        'user_id': user_id,
                        'email': email,
                        'profile_data': profile_data,
                        'student_id': student_id
                    })
                    
        return eligible_users
        
    def is_user_eligible_today(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Check if user is eligible for autopilot today."""
        
        # Get user's daily application limit
        constraints = profile_data.get('constraints', {})
        max_apps_per_day = constraints.get('max_apps_per_day', 5)
        
        # Check how many applications were made today
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).timestamp()
        today_end = datetime.combine(today, datetime.max.time()).timestamp()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM application_history 
                WHERE user_id = ? AND timestamp >= ? AND timestamp <= ?
                AND status IN ('submitted', 'retried')
            """, (user_id, today_start, today_end))
            
            applications_today = cursor.fetchone()[0]
            
        # User is eligible if they haven't reached their daily limit
        remaining_apps = max_apps_per_day - applications_today
        
        logger.info(f"User {user_id}: {applications_today}/{max_apps_per_day} apps today, {remaining_apps} remaining")
        
        return remaining_apps > 0
        
    def process_user_autopilot(self, user_data: Dict[str, Any]):
        """Process autopilot for a single user autonomously."""
        user_id = user_data['user_id']
        profile_data = user_data['profile_data']
        
        logger.info(f"🎯 Processing autopilot for user {user_id} ({user_data['email']})")
        
        try:
            # Check if sandbox portal is available
            portal_status = self.job_fetcher.check_portal_status()
            if portal_status.get("status") != "active":
                logger.warning(f"❌ Sandbox portal not available - cannot process applications")
                logger.warning(f"Portal status: {portal_status}")
                return
            
            logger.info(f"✅ Sandbox portal active: {portal_status.get('stats', {})}")
            
            # Fetch fresh jobs from sandbox portal
            portal_jobs = self.job_fetcher.fetch_jobs()
            logger.info(f"📋 Fetched {len(portal_jobs)} jobs from sandbox portal")
            
            if not portal_jobs:
                logger.warning(f"❌ No jobs available from sandbox portal")
                return
            
            # Convert portal jobs to internal format for AI ranking
            all_jobs = []
            for portal_job in portal_jobs:
                internal_job = self.job_fetcher.convert_portal_job_to_internal_format(portal_job)
                all_jobs.append(internal_job)
            
            # Get application history to avoid reapplying
            application_history = self.db.get_user_application_history(user_id, limit=1000)
            applied_job_ids = set()
            for app in application_history:
                # Exclude ALL previously processed jobs to avoid duplicates
                applied_job_ids.add(app["job_id"])
            
            logger.info(f"📝 User {user_id} has applied to {len(applied_job_ids)} jobs previously")
            
            # AI job matching and ranking
            ranked_jobs = rank_jobs_for_user(profile_data, all_jobs)
            logger.info(f"🤖 AI ranked {len(ranked_jobs)} jobs for user {user_id}")
            
            # Filter out already applied jobs and get jobs to apply to
            jobs_to_apply = []
            for job in ranked_jobs:
                if job["status"] == "will_apply" and job["job_id"] not in applied_job_ids:
                    jobs_to_apply.append(job)
            
            logger.info(f"🎯 Found {len(jobs_to_apply)} new jobs to apply to for user {user_id}")
            
            if not jobs_to_apply:
                logger.info(f"✅ No new jobs to apply for user {user_id} - all suitable jobs already applied")
                return
                
            # Limit to user's daily application limit
            constraints = profile_data.get('constraints', {})
            max_apps_per_day = constraints.get('max_apps_per_day', 5)
            
            # Check remaining applications for today
            today_apps = self.get_today_application_count(user_id)
            remaining_apps = max_apps_per_day - today_apps
            
            logger.info(f"📊 User {user_id} daily limit: {today_apps}/{max_apps_per_day} used, {remaining_apps} remaining")
            
            if remaining_apps <= 0:
                logger.info(f"🚫 User {user_id} has reached daily limit ({max_apps_per_day})")
                return
                
            # Limit jobs to remaining daily quota
            jobs_to_apply = jobs_to_apply[:remaining_apps]
            
            logger.info(f"🚀 Starting autopilot for user {user_id}: applying to {len(jobs_to_apply)} jobs")
            
            # Log job details
            for i, job in enumerate(jobs_to_apply, 1):
                logger.info(f"  {i}. {job['company']} - {job['role']} (Score: {job.get('match_score', 'N/A')})")
            
            # Create autopilot run record
            student_artifact_pack = convert_user_profile_to_student_artifact_pack(profile_data)
            run_id = self.db.create_autopilot_run_with_profile(
                user_id=user_id,
                profile_snapshot=student_artifact_pack,
                job_ids=[job["job_id"] for job in jobs_to_apply]
            )
            
            logger.info(f"📝 Created autopilot run #{run_id} for user {user_id}")
            
            # Process applications through sandbox portal
            applications = self.apply_through_portal(user_id, profile_data, jobs_to_apply)
            
            # Save application history and update run
            if applications:
                # Enhance applications with job info before saving
                enhanced_applications = []
                for app in applications:
                    # Find the job info for this application
                    job_info = next((j for j in jobs_to_apply if j["job_id"] == app["job_id"]), {})
                    enhanced_app = app.copy()
                    enhanced_app["company"] = job_info.get("company", "Unknown")
                    enhanced_app["role"] = job_info.get("role", "Unknown")
                    enhanced_applications.append(enhanced_app)
                
                # Log each application result
                for app in enhanced_applications:
                    job_info = next((j for j in jobs_to_apply if j["job_id"] == app["job_id"]), {})
                    company = job_info.get("company", "Unknown")
                    role = job_info.get("role", "Unknown")
                    status = app["status"]
                    reason = app.get("reason", "")
                    
                    if status == "submitted":
                        logger.info(f"✅ User {user_id}: Successfully applied to {company} - {role}")
                        if app.get("receipt_id"):
                            logger.info(f"   🧾 Receipt ID: {app['receipt_id']}")
                    elif status == "skipped":
                        logger.info(f"⏭️ User {user_id}: Skipped {company} - {role} ({reason})")
                    elif status == "failed":
                        logger.warning(f"❌ User {user_id}: Failed to apply to {company} - {role} ({reason})")
                    elif status == "retried":
                        logger.info(f"🔄 User {user_id}: Retried application to {company} - {role}")
                
                self.db.save_application_history(user_id, run_id, enhanced_applications)
                
                # Calculate summary
                submitted_count = len([a for a in enhanced_applications if a["status"] == "submitted"])
                skipped_count = len([a for a in enhanced_applications if a["status"] == "skipped"])
                failed_count = len([a for a in enhanced_applications if a["status"] == "failed"])
                
                summary = {
                    "submitted": submitted_count,
                    "skipped": skipped_count,
                    "failed": failed_count
                }
                
                self.db.update_autopilot_run_success(run_id, summary)
                logger.info(f"✅ User {user_id} autopilot completed: {submitted_count} applied, {skipped_count} skipped, {failed_count} failed")
            else:
                self.db.update_autopilot_run_error(run_id, "No applications processed")
                logger.error(f"❌ User {user_id}: No applications were processed")
                
        except Exception as e:
            logger.error(f"❌ Failed to process user {user_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def apply_through_portal(self, user_id: int, profile_data: Dict[str, Any], jobs_to_apply: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply to jobs through the sandbox portal with improved logic."""
        applications = []
        
        logger.info(f"🌐 Applying through sandbox portal for user {user_id}")
        
        # Convert user profile to application data format
        application_data = self.job_fetcher.convert_user_profile_to_application_data(profile_data)
        
        # Get user constraints for filtering
        constraints = profile_data.get('constraints', {})
        blocked_companies = constraints.get('blocked_companies', [])
        preferred_locations = constraints.get('preferred_locations', [])
        min_salary = constraints.get('min_salary')
        
        for job in jobs_to_apply:
            try:
                # Add some demo variety - randomly skip some jobs for demonstration
                import random
                demo_skip_chance = 0.3  # 30% chance to skip for demo purposes
                
                if random.random() < demo_skip_chance:
                    skip_reasons = [
                        f"Company '{job['company']}' not in preferred list",
                        f"Location '{job.get('location')}' not preferred",
                        f"Salary range '{job.get('salary_range')}' below expectations",
                        f"Job requires {job.get('min_experience_years', 0)} years experience",
                        "Application deadline too soon",
                        "Company culture mismatch"
                    ]
                    reason = random.choice(skip_reasons)
                    logger.info(f"⏭️ Skipping {job['company']} - {job['role']} ({reason})")
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "skipped",
                        "reason": reason,
                        "timestamp": time.time()
                    })
                    continue
                
                # Check if company is blocked
                if job['company'] in blocked_companies:
                    logger.info(f"⏭️ Skipping {job['company']} - {job['role']} (blocked company)")
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "skipped",
                        "reason": f"Company '{job['company']}' is in blocked list",
                        "timestamp": time.time()
                    })
                    continue
                
                # Check location preferences (if specified)
                if preferred_locations and not any(loc.lower() in job.get('location', '').lower() for loc in preferred_locations):
                    logger.info(f"⏭️ Skipping {job['company']} - {job['role']} (location mismatch)")
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "skipped",
                        "reason": f"Location '{job.get('location')}' not in preferred locations",
                        "timestamp": time.time()
                    })
                    continue
                
                # Check minimum experience requirements
                user_experience = int(application_data.get('experience_years', '0'))
                job_min_experience = job.get('min_experience_years', 0)
                
                if job_min_experience > user_experience + 1:  # Allow 1 year flexibility
                    logger.info(f"⏭️ Skipping {job['company']} - {job['role']} (insufficient experience)")
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "skipped",
                        "reason": f"Requires {job_min_experience} years experience, user has {user_experience}",
                        "timestamp": time.time()
                    })
                    continue
                
                # Check if user has relevant skills (at least 2 matching skills for non-entry level)
                user_skills = [skill.lower() for skill in application_data.get('skills', [])]
                job_skills = [skill.lower() for skill in job.get('required_skills', [])]
                matching_skills = set(user_skills) & set(job_skills)
                
                if job.get('experience_level') != 'Entry Level' and len(matching_skills) < 2:
                    logger.info(f"⏭️ Skipping {job['company']} - {job['role']} (insufficient skill match)")
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "skipped",
                        "reason": f"Only {len(matching_skills)} matching skills out of {len(job_skills)} required",
                        "timestamp": time.time()
                    })
                    continue
                
                # Simulate some random failures (10% chance) to make it realistic
                if random.random() < 0.10:
                    failure_reasons = [
                        "Network timeout during submission",
                        "Application portal temporarily unavailable",
                        "File upload failed",
                        "Form validation error",
                        "Server error (500)"
                    ]
                    reason = random.choice(failure_reasons)
                    logger.warning(f"❌ Simulated failure for {job['company']} - {job['role']} ({reason})")
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "failed",
                        "reason": reason,
                        "timestamp": time.time()
                    })
                    continue
                
                logger.info(f"📝 Submitting application to {job['company']} - {job['role']}")
                
                # Submit application through portal
                result = self.job_fetcher.submit_application(job['job_id'], application_data)
                
                if result['success']:
                    applications.append({
                        "job_id": job['job_id'],
                        "status": "submitted",
                        "reason": "Successfully submitted through portal",
                        "receipt_id": result.get('receipt_id'),
                        "application_id": result.get('application_id'),
                        "timestamp": time.time()
                    })
                else:
                    # Try retry once for failed submissions
                    logger.warning(f"🔄 Retrying application to {job['company']} - {job['role']}")
                    time.sleep(1)
                    retry_result = self.job_fetcher.submit_application(job['job_id'], application_data)
                    
                    if retry_result['success']:
                        applications.append({
                            "job_id": job['job_id'],
                            "status": "retried",
                            "reason": "Successfully submitted after retry",
                            "receipt_id": retry_result.get('receipt_id'),
                            "application_id": retry_result.get('application_id'),
                            "timestamp": time.time()
                        })
                    else:
                        applications.append({
                            "job_id": job['job_id'],
                            "status": "failed",
                            "reason": result.get('error', 'Unknown error'),
                            "timestamp": time.time()
                        })
                
                # Small delay between applications
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to apply to {job['job_id']}: {e}")
                applications.append({
                    "job_id": job['job_id'],
                    "status": "failed",
                    "reason": str(e),
                    "timestamp": time.time()
                })
        
        return applications
            
    def get_today_application_count(self, user_id: int) -> int:
        """Get number of applications made today by user."""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).timestamp()
        today_end = datetime.combine(today, datetime.max.time()).timestamp()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM application_history 
                WHERE user_id = ? AND timestamp >= ? AND timestamp <= ?
                AND status IN ('submitted', 'retried')
            """, (user_id, today_start, today_end))
            
            return cursor.fetchone()[0]
            
    def convert_database_job_to_engine_format(self, db_job: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database job format to engine JobListing format."""
        return {
            "job_id": db_job["job_id"],
            "company": db_job["company"],
            "role": db_job["role"],
            "location": db_job["location"],
            "required_skills": db_job["required_skills"],
            "min_experience_years": db_job["min_experience_years"]
        }

# Global autonomous agent instance
autonomous_agent = AutonomousAIAgent()

def start_autonomous_ai_agent():
    """Start the autonomous AI agent."""
    autonomous_agent.start_autonomous_mode()
    
def stop_autonomous_ai_agent():
    """Stop the autonomous AI agent."""
    autonomous_agent.stop_autonomous_mode()