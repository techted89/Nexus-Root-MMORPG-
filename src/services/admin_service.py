"""
Service for handling admin-related tasks
"""

import sqlite3
import uuid
from typing import List, Tuple
from ..repositories.sqlite_player_repository import SQLitePlayerRepository
from ..core.exceptions import NexusException
from ..core.logger import NexusLogger

class AdminService:
    """
    Service for handling admin-related tasks
    """

    def __init__(self, player_repository: SQLitePlayerRepository):
        """Initialize the AdminService"""
        self.player_repository = player_repository
        self.logger = NexusLogger.get_logger("admin_service")

    def get_all_players(self, search: str = None, sort: str = "name", order: str = "asc") -> List:
        """Get all players"""
        try:
            players = self.player_repository.find_all()

            if search:
                players = [p for p in players if search.lower() in p.name.lower()]

            if sort:
                players.sort(key=lambda p: p.to_dict().get(sort, 0), reverse=order == "desc")

            return players
        except NexusException as e:
            self.logger.error(f"Failed to get all players: {e}")
            raise

    def ban_player(self, player_id: str) -> Tuple[bool, str]:
        """Ban a player"""
        try:
            player = self.player_repository.find_by_id(player_id)
            if not player:
                return False, "Player not found"

            # Add a 'banned' flag to the player's data
            player.data["banned"] = True
            self.player_repository.save(player)

            return True, f"Player {player.name} has been banned"
        except NexusException as e:
            self.logger.error(f"Failed to ban player {player_id}: {e}")
            raise

    def unban_player(self, player_id: str) -> Tuple[bool, str]:
        """Unban a player"""
        try:
            player = self.player_repository.find_by_id(player_id)
            if not player:
                return False, "Player not found"

            # Remove the 'banned' flag from the player's data
            if "banned" in player.data:
                del player.data["banned"]
                self.player_repository.save(player)
                return True, f"Player {player.name} has been unbanned"

            return False, f"Player {player.name} is not banned"
        except NexusException as e:
            self.logger.error(f"Failed to unban player {player_id}: {e}")
            raise

    def get_banned_players(self) -> List:
        """Get all banned players"""
        try:
            players = self.player_repository.find_all()
            banned_players = [p for p in players if p.data.get("banned")]
            return banned_players
        except NexusException as e:
            self.logger.error(f"Failed to get banned players: {e}")
            raise

    def send_announcement(self, message: str):
        """Send an announcement to all online players"""
        try:
            with open("announcement.txt", "w") as f:
                f.write(message)
            self.logger.info(f"Announcement sent: {message}")
        except IOError as e:
            self.logger.error(f"Failed to send announcement: {e}")
            raise

    def ban_ip(self, ip_address: str) -> Tuple[bool, str]:
        """Ban an IP address"""
        try:
            with sqlite3.connect(self.player_repository.db_path) as conn:
                conn.execute(
                    "INSERT INTO banned_ips (id, ip_address) VALUES (?, ?)",
                    (str(uuid.uuid4()), ip_address)
                )
                conn.commit()
            return True, f"IP address {ip_address} has been banned"
        except sqlite3.IntegrityError:
            return False, f"IP address {ip_address} is already banned"
        except sqlite3.Error as e:
            self.logger.error(f"Failed to ban IP address {ip_address}: {e}")
            raise

    def unban_ip(self, ip_address: str) -> Tuple[bool, str]:
        """Unban an IP address"""
        try:
            with sqlite3.connect(self.player_repository.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM banned_ips WHERE ip_address = ?",
                    (ip_address,)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    return True, f"IP address {ip_address} has been unbanned"
                return False, f"IP address {ip_address} is not banned"
        except sqlite3.Error as e:
            self.logger.error(f"Failed to unban IP address {ip_address}: {e}")
            raise