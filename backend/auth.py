"""
Authentication system for the persistent job application platform.
Simple session-based authentication for now.
"""
import hashlib
import secrets
from typing import Optional, Dict, Any
from backend.database import PersistentDatabase


class AuthManager:
    """Simple authentication manager."""
    
    def __init__(self, db: PersistentDatabase):
        self.db = db
        self.active_sessions: Dict[str, int] = {}  # token -> user_id
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = "job_app_platform_salt"  # In production, use random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def register_user(self, email: str, password: str) -> tuple[bool, str, Optional[int]]:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                return False, "User with this email already exists", None
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            user_id = self.db.create_user(email, password_hash)
            
            return True, "User registered successfully", user_id
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
    
    def login_user(self, email: str, password: str) -> tuple[bool, str, Optional[str], Optional[int]]:
        """Login user and return session token."""
        try:
            # Get user by email
            user = self.db.get_user_by_email(email)
            if not user:
                return False, "Invalid email or password", None, None
            
            # Check if user is active
            if not user["is_active"]:
                return False, "Account is deactivated", None, None
            
            # Verify password
            password_hash = self.hash_password(password)
            if password_hash != user["password_hash"]:
                return False, "Invalid email or password", None, None
            
            # Generate session token
            token = secrets.token_urlsafe(32)
            self.active_sessions[token] = user["id"]
            
            # Update last login
            self.db.update_last_login(user["id"])
            
            return True, "Login successful", token, user["id"]
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None, None
    
    def logout_user(self, token: str) -> bool:
        """Logout user by removing session token."""
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False
    
    def get_user_from_token(self, token: str) -> Optional[int]:
        """Get user ID from session token."""
        return self.active_sessions.get(token)
    
    def is_authenticated(self, token: str) -> bool:
        """Check if token is valid."""
        return token in self.active_sessions
    
    def require_auth(self, token: Optional[str]) -> tuple[bool, Optional[int], str]:
        """Require authentication and return user ID."""
        if not token:
            return False, None, "Authentication token required"
        
        user_id = self.get_user_from_token(token)
        if not user_id:
            return False, None, "Invalid or expired token"
        
        return True, user_id, "Authenticated"