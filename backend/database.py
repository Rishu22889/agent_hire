"""
Database models and connection for the persistent job application platform.
Supports user profiles, job listings, and application history.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid


class PersistentDatabase:
    """SQLite database manager for the persistent job application platform."""
    
    def __init__(self, db_path: str = "../data/platform.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self.init_tables()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def validate_user_profile(self, profile: dict):
        """Validate user profile against UserProfile schema (NEW FORMAT)."""
        from schemas.user_profile_schema import UserProfile
        
        try:
            # Validate using the new UserProfile schema
            validated_profile = UserProfile(**profile)
            return True
        except Exception as e:
            raise ValueError(f"UserProfile validation failed: {e}")
    
    def validate_student_profile(self, profile: dict):
        """Validate student profile against canonical schema (LEGACY - for engine execution only)."""
        REQUIRED_TOP_LEVEL_KEYS = [
            "source_resume_hash",
            "skill_vocab", 
            "education",
            "projects",
            "constraints"
        ]
        
        for key in REQUIRED_TOP_LEVEL_KEYS:
            if key not in profile:
                raise ValueError(f"StudentArtifactPack invalid: missing '{key}'")
        
        # Education
        if not isinstance(profile["education"], list):
            raise ValueError("StudentArtifactPack invalid: education must be a list")
        
        # Projects with bullets
        if not isinstance(profile["projects"], list):
            raise ValueError("StudentArtifactPack invalid: projects must be a list")
        
        for project in profile["projects"]:
            if "bullets" not in project:
                raise ValueError("StudentArtifactPack invalid: project missing bullets")
            
            for bullet in project["bullets"]:
                if not bullet.get("verified", False):
                    raise ValueError("StudentArtifactPack invalid: all bullets must be verified for engine execution")
        
        # Constraints (AUTONOMY BLOCKER)
        constraints = profile["constraints"]
        REQUIRED_CONSTRAINT_KEYS = [
            "min_match_score",
            "max_apps_per_day"
        ]
        
        for key in REQUIRED_CONSTRAINT_KEYS:
            if key not in constraints:
                raise ValueError(f"Autopilot blocked: missing constraint '{key}'")
        
        if constraints["min_match_score"] < 0 or constraints["min_match_score"] > 1:
            raise ValueError("Invalid min_match_score: must be between 0 and 1")
        
        if constraints["max_apps_per_day"] <= 0:
            raise ValueError("Invalid max_apps_per_day: must be positive")
        
        return True
    
    def init_tables(self):
        """Initialize database tables for persistent platform."""
        with self.get_connection() as conn:
            conn.executescript("""
                -- Users table (authentication and basic info)
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
                
                -- User profiles (SINGLE SOURCE OF TRUTH)
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    student_id TEXT UNIQUE NOT NULL,
                    profile_data TEXT NOT NULL,  -- JSON blob of complete profile
                    resume_hash TEXT,
                    resume_text TEXT,  -- Raw extracted text
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                
                -- Job listings (persistent job database)
                CREATE TABLE IF NOT EXISTS job_listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    location TEXT NOT NULL,
                    required_skills TEXT NOT NULL,  -- JSON array
                    min_experience_years INTEGER NOT NULL,
                    description TEXT,
                    salary_range TEXT,
                    job_type TEXT,  -- full-time, part-time, internship
                    posted_date TIMESTAMP,
                    expires_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Autopilot runs (execution tracking)
                CREATE TABLE IF NOT EXISTS autopilot_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    profile_snapshot TEXT NOT NULL,  -- JSON snapshot of profile at run time
                    job_ids TEXT NOT NULL,  -- JSON array of job IDs processed
                    status TEXT NOT NULL,  -- running, completed, failed
                    summary_data TEXT,  -- JSON summary (queued, skipped, submitted, etc.)
                    log_path TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                
                -- Application history (CRITICAL - persistent record)
                CREATE TABLE IF NOT EXISTS application_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    run_id INTEGER NOT NULL,
                    job_id TEXT NOT NULL,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,  -- queued, skipped, submitted, failed, retried
                    skip_reason TEXT,
                    receipt_id TEXT,
                    timestamp REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (run_id) REFERENCES autopilot_runs (id) ON DELETE CASCADE
                );
                
                -- Artifact workflow tables (NEW - for approval workflow)
                CREATE TABLE IF NOT EXISTS draft_artifacts (
                    id TEXT PRIMARY KEY,  -- UUID
                    user_id INTEGER NOT NULL,
                    student_artifact_pack TEXT NOT NULL,  -- JSON blob
                    status TEXT NOT NULL DEFAULT 'DRAFT',
                    source_profile_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS artifact_snapshots (
                    id TEXT PRIMARY KEY,  -- UUID
                    user_id INTEGER NOT NULL,
                    student_artifact_pack TEXT NOT NULL,  -- JSON blob (immutable)
                    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_resume_hash TEXT NOT NULL,
                    source_profile_hash TEXT NOT NULL,
                    frozen BOOLEAN DEFAULT TRUE,  -- Always true for snapshots
                    approval_metadata TEXT NOT NULL,  -- JSON blob with user confirmation
                    integrity_hash TEXT NOT NULL,  -- For validation
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
                CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles (user_id);
                CREATE INDEX IF NOT EXISTS idx_profiles_student_id ON user_profiles (student_id);
                CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON job_listings (job_id);
                CREATE INDEX IF NOT EXISTS idx_jobs_company ON job_listings (company);
                CREATE INDEX IF NOT EXISTS idx_jobs_active ON job_listings (is_active);
                CREATE INDEX IF NOT EXISTS idx_runs_user_id ON autopilot_runs (user_id);
                CREATE INDEX IF NOT EXISTS idx_history_user_id ON application_history (user_id);
                CREATE INDEX IF NOT EXISTS idx_history_job_id ON application_history (job_id);
                CREATE INDEX IF NOT EXISTS idx_history_status ON application_history (status);
                CREATE INDEX IF NOT EXISTS idx_draft_artifacts_user_id ON draft_artifacts (user_id);
                CREATE INDEX IF NOT EXISTS idx_artifact_snapshots_user_id ON artifact_snapshots (user_id);
                CREATE INDEX IF NOT EXISTS idx_artifact_snapshots_approved_at ON artifact_snapshots (approved_at);
            """)
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, email: str, password_hash: str) -> int:
        """Create a new user account."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
            """, (email, password_hash))
            return cursor.lastrowid
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, password_hash, created_at, last_login, is_active
                FROM users WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "password_hash": row[2],
                    "created_at": row[3],
                    "last_login": row[4],
                    "is_active": bool(row[5])
                }
            return None
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            """, (user_id,))
    
    # ==================== USER PROFILES (SINGLE SOURCE OF TRUTH) ====================
    
    def create_user_profile(self, user_id: int, student_id: str, profile_data: Dict[str, Any], 
                           resume_hash: str = None, resume_text: str = None) -> int:
        """Create a new user profile (SINGLE SOURCE OF TRUTH)."""
        # FAIL FAST: Validate profile before creation using NEW schema
        self.validate_user_profile(profile_data)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_profiles (user_id, student_id, profile_data, resume_hash, resume_text)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, student_id, json.dumps(profile_data), resume_hash, resume_text))
            return cursor.lastrowid
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, student_id, profile_data, resume_hash, resume_text, created_at, updated_at
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "user_id": user_id,
                    "student_id": row[1],
                    "profile_data": json.loads(row[2]),
                    "resume_hash": row[3],
                    "resume_text": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile (can be edited anytime)."""
        # FAIL FAST: Validate profile before update using NEW schema
        self.validate_user_profile(profile_data)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_profiles 
                SET profile_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (json.dumps(profile_data), user_id))
            
            if cursor.rowcount == 0:
                raise RuntimeError(f"Profile update failed: no profile found for user_id {user_id}")
            
            return True
    
    def get_profile_by_student_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get profile by student ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, profile_data, resume_hash, resume_text, created_at, updated_at
                FROM user_profiles WHERE student_id = ?
            """, (student_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "user_id": row[0],
                    "student_id": student_id,
                    "profile_data": json.loads(row[1]),
                    "resume_hash": row[2],
                    "resume_text": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                }
            return None
    
    # ==================== JOB LISTINGS ====================
    
    def add_job_listing(self, job_data: Dict[str, Any]) -> int:
        """Add a new job listing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO job_listings 
                (job_id, company, role, location, required_skills, min_experience_years, 
                 description, salary_range, job_type, posted_date, expires_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data["job_id"],
                job_data["company"],
                job_data["role"],
                job_data["location"],
                json.dumps(job_data["required_skills"]),
                job_data["min_experience_years"],
                job_data.get("description"),
                job_data.get("salary_range"),
                job_data.get("job_type", "full-time"),
                job_data.get("posted_date"),
                job_data.get("expires_date")
            ))
            return cursor.lastrowid
    
    def get_active_job_listings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active job listings."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_id, company, role, location, required_skills, min_experience_years,
                       description, salary_range, job_type, posted_date, expires_date, created_at
                FROM job_listings 
                WHERE is_active = TRUE
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            jobs = []
            for row in cursor.fetchall():
                jobs.append({
                    "job_id": row[0],
                    "company": row[1],
                    "role": row[2],
                    "location": row[3],
                    "required_skills": json.loads(row[4]),
                    "min_experience_years": row[5],
                    "description": row[6],
                    "salary_range": row[7],
                    "job_type": row[8],
                    "posted_date": row[9],
                    "expires_date": row[10],
                    "created_at": row[11]
                })
            return jobs
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job listing by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_id, company, role, location, required_skills, min_experience_years,
                       description, salary_range, job_type, posted_date, expires_date
                FROM job_listings WHERE job_id = ? AND is_active = TRUE
            """, (job_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "job_id": row[0],
                    "company": row[1],
                    "role": row[2],
                    "location": row[3],
                    "required_skills": json.loads(row[4]),
                    "min_experience_years": row[5],
                    "description": row[6],
                    "salary_range": row[7],
                    "job_type": row[8],
                    "posted_date": row[9],
                    "expires_date": row[10]
                }
            return None
    
    # ==================== AUTOPILOT RUNS ====================
    
    def create_autopilot_run(self, user_id: int, job_ids: List[str]) -> int:
        """Create new autopilot run record (simplified version)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO autopilot_runs (user_id, job_ids, status, profile_snapshot)
                VALUES (?, ?, 'running', '{}')
            """, (user_id, json.dumps(job_ids)))
            return cursor.lastrowid
    
    def create_autopilot_run_with_profile(self, user_id: int, profile_snapshot: Dict[str, Any], job_ids: List[str]) -> int:
        """Create new autopilot run record with profile validation."""
        # FAIL FAST: Validate profile snapshot before autopilot (must be StudentArtifactPack format)
        self.validate_student_profile(profile_snapshot)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO autopilot_runs (user_id, profile_snapshot, job_ids, status)
                VALUES (?, ?, ?, 'running')
            """, (user_id, json.dumps(profile_snapshot), json.dumps(job_ids)))
            return cursor.lastrowid
    
    def update_autopilot_run_success(self, run_id: int, summary_data: Dict[str, Any]):
        """Mark autopilot run as completed successfully."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE autopilot_runs 
                SET status = 'completed', summary_data = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(summary_data), run_id))
    
    def update_autopilot_run_error(self, run_id: int, error_message: str):
        """Mark autopilot run as failed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE autopilot_runs 
                SET status = 'failed', summary_data = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps({"error": error_message}), run_id))
    
    def complete_autopilot_run(self, run_id: int, summary_data: Dict[str, Any], log_path: str):
        """Mark autopilot run as completed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE autopilot_runs 
                SET status = 'completed', summary_data = ?, log_path = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(summary_data), log_path, run_id))
    
    def fail_autopilot_run(self, run_id: int, error_message: str):
        """Mark autopilot run as failed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE autopilot_runs 
                SET status = 'failed', summary_data = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps({"error": error_message}), run_id))
    
    def get_user_autopilot_runs(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get autopilot runs for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, job_ids, status, summary_data, log_path, started_at, completed_at
                FROM autopilot_runs 
                WHERE user_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            runs = []
            for row in cursor.fetchall():
                runs.append({
                    "id": row[0],
                    "job_ids": json.loads(row[1]),
                    "status": row[2],
                    "summary_data": json.loads(row[3]) if row[3] else {},
                    "log_path": row[4],
                    "started_at": row[5],
                    "completed_at": row[6]
                })
            return runs
    
    # ==================== APPLICATION HISTORY (CRITICAL) ====================
    
    def save_application_history(self, user_id: int, run_id: int, applications: List[Dict[str, Any]]):
        """Save application history from tracker."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for app in applications:
                # Use company and role from application data if available, otherwise lookup
                company = app.get("company")
                role = app.get("role")
                
                if not company or not role:
                    # Fallback to job lookup if not provided
                    job_details = self.get_job_by_id(app["job_id"])
                    company = company or (job_details["company"] if job_details else "Unknown")
                    role = role or (job_details["role"] if job_details else "Unknown")
                
                cursor.execute("""
                    INSERT INTO application_history 
                    (user_id, run_id, job_id, company, role, status, skip_reason, receipt_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    run_id,
                    app["job_id"],
                    company,
                    role,
                    app["status"],
                    app.get("reason"),
                    app.get("receipt_id"),
                    app["timestamp"]
                ))
    
    def get_user_application_history(self, user_id: int, limit: int = 100, status_filter: str = None) -> List[Dict[str, Any]]:
        """Get application history for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, run_id, job_id, company, role, status, skip_reason, receipt_id, timestamp, created_at
                FROM application_history 
                WHERE user_id = ?
            """
            params = [user_id]
            
            if status_filter:
                query += " AND status = ?"
                params.append(status_filter)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "id": row[0],
                    "run_id": row[1],
                    "job_id": row[2],
                    "company": row[3],
                    "role": row[4],
                    "status": row[5],
                    "skip_reason": row[6],
                    "receipt_id": row[7],
                    "timestamp": row[8],
                    "created_at": row[9]
                })
            return history
    
    def delete_application_history_entry(self, user_id: int, history_id: int) -> bool:
        """Delete an application history entry (UI only - does NOT affect backend safety logs)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM application_history 
                WHERE id = ? AND user_id = ?
            """, (history_id, user_id))
            return cursor.rowcount > 0
    
    def clear_user_application_history(self, user_id: int) -> int:
        """
        Clear all application history for a user when profile/resume is updated.
        This allows the user to reapply to jobs with their updated profile.
        Returns the number of entries cleared.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM application_history 
                WHERE user_id = ?
            """, (user_id,))
            return cursor.rowcount
    
    def get_application_stats(self, user_id: int) -> Dict[str, int]:
        """Get application statistics for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM application_history 
                WHERE user_id = ?
                GROUP BY status
            """, (user_id,))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = row[1]
            
            return stats

    # ==================== ARTIFACT WORKFLOW (NEW) ====================
    
    def save_draft_artifact(self, draft_id: str, user_id: int, student_artifact_pack: Dict[str, Any], 
                           source_profile_hash: str) -> bool:
        """Save draft artifact to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO draft_artifacts 
                (id, user_id, student_artifact_pack, source_profile_hash)
                VALUES (?, ?, ?, ?)
            """, (draft_id, user_id, json.dumps(student_artifact_pack), source_profile_hash))
            return cursor.rowcount > 0
    
    def get_draft_artifact(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current draft artifact for user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, student_artifact_pack, status, source_profile_hash, created_at
                FROM draft_artifacts 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "user_id": user_id,
                    "student_artifact_pack": json.loads(row[1]),
                    "status": row[2],
                    "source_profile_hash": row[3],
                    "created_at": row[4]
                }
            return None
    
    def save_artifact_snapshot(self, snapshot_id: str, user_id: int, student_artifact_pack: Dict[str, Any],
                              source_resume_hash: str, source_profile_hash: str, 
                              approval_metadata: Dict[str, Any], integrity_hash: str) -> bool:
        """Save approved artifact snapshot to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO artifact_snapshots 
                (id, user_id, student_artifact_pack, source_resume_hash, source_profile_hash, 
                 approval_metadata, integrity_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id, user_id, json.dumps(student_artifact_pack), 
                source_resume_hash, source_profile_hash, 
                json.dumps(approval_metadata), integrity_hash
            ))
            return cursor.rowcount > 0
    
    def get_current_artifact_snapshot(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current approved artifact snapshot for user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, student_artifact_pack, approved_at, source_resume_hash, 
                       source_profile_hash, approval_metadata, integrity_hash
                FROM artifact_snapshots 
                WHERE user_id = ?
                ORDER BY approved_at DESC
                LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "user_id": user_id,
                    "student_artifact_pack": json.loads(row[1]),
                    "approved_at": row[2],
                    "source_resume_hash": row[3],
                    "source_profile_hash": row[4],
                    "frozen": True,  # Always true for snapshots
                    "approval_metadata": json.loads(row[5]),
                    "integrity_hash": row[6]
                }
            return None
    
    def delete_draft_artifacts(self, user_id: int) -> bool:
        """Delete all draft artifacts for user (cleanup after approval)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM draft_artifacts WHERE user_id = ?
            """, (user_id,))
            return cursor.rowcount > 0