"""
Admin API for managing the game
"""

from typing import Dict, Any, List, Optional
from ..services.player_service import PlayerService
from ..services.admin_service import AdminService
from ..core.exceptions import NexusException, AuthenticationError
from ..core.logger import NexusLogger

class AdminAPI:
    """
    Admin API for managing the game
    """

    def __init__(self, player_service: PlayerService, admin_service: AdminService):
        """Initialize the Admin API"""
        self.player_service = player_service
        self.admin_service = admin_service
        self.logger = NexusLogger.get_logger("admin_api")

    def get_all_players(self, search: str = None, sort: str = "name", order: str = "asc") -> Dict[str, Any]:
        """Get all players"""
        try:
            players = self.admin_service.get_all_players(search, sort, order)
            return {
                "success": True,
                "data": [player.to_dict() for player in players]
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def ban_ip(self, ip_address: str) -> Dict[str, Any]:
        """Ban an IP address"""
        try:
            success, message = self.admin_service.ban_ip(ip_address)
            return {
                "success": success,
                "message": message
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def unban_ip(self, ip_address: str) -> Dict[str, Any]:
        """Unban an IP address"""
        try:
            success, message = self.admin_service.unban_ip(ip_address)
            return {
                "success": success,
                "message": message
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def get_player_details(self, player_id: str) -> Dict[str, Any]:
        """Get player details"""
        try:
            player = self.player_service.get_player(player_id)
            if not player:
                return {
                    "success": False,
                    "error": "Player not found"
                }

            return {
                "success": True,
                "data": player.to_dict()
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def ban_player(self, player_id: str) -> Dict[str, Any]:
        """Ban a player"""
        try:
            success, message = self.admin_service.ban_player(player_id)
            return {
                "success": success,
                "message": message
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def unban_player(self, player_id: str) -> Dict[str, Any]:
        """Unban a player"""
        try:
            success, message = self.admin_service.unban_player(player_id)
            return {
                "success": success,
                "message": message
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def get_banned_players(self) -> Dict[str, Any]:
        """Get banned players"""
        try:
            banned_players = self.admin_service.get_banned_players()
            return {
                "success": True,
                "data": banned_players
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def send_announcement(self, message: str) -> Dict[str, Any]:
        """Send an announcement to all online players"""
        try:
            self.admin_service.send_announcement(message)
            return {
                "success": True,
                "message": "Announcement sent successfully"
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }