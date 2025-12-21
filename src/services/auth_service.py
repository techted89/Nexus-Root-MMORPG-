import sqlite3
import hashlib
import uuid
import os
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

    def _hash_password(self, password: str, salt: bytes = None) -> str:
        """Hash password using PBKDF2 with SHA-256"""
        if salt is None:
            salt = os.urandom(16)

        # 100,000 iterations for reasonable security/performance balance
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ":" + key.hex()

    def _verify_password(self, stored_hash: str, password: str) -> bool:
        """Verify password against stored hash"""
        try:
            # Handle legacy SHA-256 hashes (64 chars hex)
            if len(stored_hash) == 64 and ":" not in stored_hash:
                legacy_hash = hashlib.sha256(password.encode()).hexdigest()
                return legacy_hash == stored_hash

            salt_hex, key_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return new_key.hex() == key_hex
        except (ValueError, AttributeError):
            return False

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

        # Hash the password (PBKDF2)
        password_hash = self._hash_password(password)

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

        if not password_hash or not self._verify_password(password_hash, password):
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