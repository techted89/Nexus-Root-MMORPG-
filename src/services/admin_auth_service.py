import sqlite3
import hashlib
import uuid
from ..core.exceptions import AuthenticationError

class AdminAuthService:
    """Service for handling admin authentication"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_admin_user(self, username: str):
        """Get an admin user from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id, password_hash FROM admin_users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                return row if row else None
        except sqlite3.Error as e:
            raise AuthenticationError(f"Database error: {e}")

    def authenticate(self, username: str, password: str) -> str:
        """Authenticate an admin user and return a session token"""
        admin_user = self._get_admin_user(username)
        if not admin_user:
            raise AuthenticationError("Invalid username or password")

        admin_id, password_hash = admin_user
        if password_hash != hashlib.sha256(password.encode()).hexdigest():
            raise AuthenticationError("Invalid username or password")

        session_token = str(uuid.uuid4())
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO sessions (id, admin_id, token) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), admin_id, session_token)
                )
                conn.commit()
            return session_token
        except sqlite3.Error as e:
            raise AuthenticationError(f"Database error: {e}")

    def is_authenticated(self, token: str) -> bool:
        """Check if a session token is valid"""
        if not token:
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM sessions WHERE token = ?",
                    (token,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            return False

    def logout(self, token: str):
        """Logout an admin user by deleting their session token"""
        if not token:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM sessions WHERE token = ?",
                    (token,)
                )
                conn.commit()
        except sqlite3.Error as e:
            # Log the error, but don't raise it to the client
            print(f"Error logging out: {e}")