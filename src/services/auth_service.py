import sqlite3
import hashlib
import uuid
from ..core.exceptions import AuthenticationError, ValidationError
from ..repositories.sqlite_player_repository import SQLitePlayerRepository

class AuthService:
    """Service for handling user authentication"""

    def __init__(self, db_path: str, player_repository: SQLitePlayerRepository):
        self.db_path = db_path
        self.player_repository = player_repository

    def _get_player_by_username(self, username: str):
        """Get a player by username from the database"""
        player = self.player_repository.find_by_name(username)
        if player:
            return player.id, player.password_hash
        return None

    def register(self, username: str, password: str) -> str:
        """Register a new player"""
        # Validate username and password
        if not username or len(username) < 2 or len(username) > 20:
            raise ValidationError("Username must be 2-20 characters")
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        # Check if username is taken
        if self.player_repository.find_by_name(username):
            raise ValidationError("Username is already taken")

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Create a new player
        from ..models.player import Player
        player = Player(name=username)
        player.password_hash = password_hash
        self.player_repository.save(player)
        return "Registration successful."

    def login(self, username: str, password: str) -> str:
        """Authenticate a player and return a session token"""
        player_data = self._get_player_by_username(username)
        if not player_data:
            raise AuthenticationError("Invalid username or password")

        player_id, password_hash = player_data
        if not password_hash or password_hash != hashlib.sha256(password.encode()).hexdigest():
            raise AuthenticationError("Invalid username or password")

        session_token = str(uuid.uuid4())
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO sessions (id, player_id, token) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), player_id, session_token)
                )
                conn.commit()
            return session_token
        except sqlite3.Error as e:
            raise AuthenticationError(f"Database error: {e}")