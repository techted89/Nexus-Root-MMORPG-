from typing import Dict, Any
from ..services.auth_service import AuthService
from ..core.exceptions import NexusException

class AuthAPI:
    """API for handling user authentication"""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new player"""
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"success": False, "error": "Missing username or password"}

        try:
            message = self.auth_service.register(username, password)
            return {"success": True, "message": message}
        except NexusException as e:
            return {"success": False, "error": e.message}

    def login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate a player and return a session token"""
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"success": False, "error": "Missing username or password"}

        try:
            token = self.auth_service.login(username, password)
            return {"success": True, "token": token}
        except NexusException as e:
            return {"success": False, "error": e.message}