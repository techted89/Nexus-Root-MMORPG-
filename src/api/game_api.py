"""
Game API for external integration and embedding
"""

from typing import Dict, Any, List, Optional
from ..services.player_service import PlayerService
from ..services.command_service import CommandService
from ..services.mission_service import MissionService
from ..repositories.sqlite_player_repository import SQLitePlayerRepository
from ..repositories.sqlite_mission_repository import SQLiteMissionRepository
from ..core.events import EventBus
from ..core.config import NexusConfig
from ..core.exceptions import NexusException, ValidationError, AuthenticationError
from ..core.logger import NexusLogger

class GameAPI:
    """
    Main Game API for external integration
    
    This class provides a clean interface for embedding the Nexus Root game
    into other applications or accessing game functionality programmatically.
    """
    
    def __init__(self, config: NexusConfig = None):
        """Initialize the Game API"""
        self.config = config or NexusConfig.load_from_file()
        self.logger = NexusLogger.get_logger("game_api")
        self.event_bus = EventBus()
        
        # Initialize repositories
        self.player_repository = SQLitePlayerRepository(self.config.database.database)
        self.mission_repository = SQLiteMissionRepository(self.config.database.database)
        
        # Initialize services
        self.player_service = PlayerService(self.player_repository, self.event_bus)
        self.command_service = CommandService(self.event_bus, self.player_service)
        self.mission_service = MissionService(self.mission_repository, self.event_bus)
        
        # Setup event handlers
        self._setup_event_handlers()
        
        self.logger.info("Game API initialized")
    
    def _setup_event_handlers(self):
        """Setup event handlers for cross-service communication"""
        from ..core.events import GameEvents
        
        # Handle command execution for mission progress
        class CommandMissionHandler:
            def __init__(self, mission_service, player_service):
                self.mission_service = mission_service
                self.player_service = player_service
            
            def handle(self, event):
                player = self.player_service.get_player(event.data["player_id"])
                if player:
                    self.mission_service.handle_command_execution(
                        player,
                        event.data["command"],
                        event.data["success"],
                        event.data
                    )
                return True
        
        self.event_bus.subscribe(
            GameEvents.COMMAND_EXECUTED,
            CommandMissionHandler(self.mission_service, self.player_service)
        )
    
    # Player Management API
    
    def create_player(self, name: str, is_vip: bool = False, session_id: str = None) -> Dict[str, Any]:
        """Create a new player"""
        try:
            player = self.player_service.create_player(name, is_vip, session_id)
            return {
                "success": True,
                "data": player.get_summary(),
                "message": f"Player '{name}' created successfully"
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def get_announcement(self) -> Dict[str, Any]:
        """Get the current announcement"""
        try:
            with open("announcement.txt", "r") as f:
                message = f.read()
            return {
                "success": True,
                "data": message
            }
        except FileNotFoundError:
            return {
                "success": True,
                "data": ""
            }
        except IOError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def authenticate_player(self, name: str, session_id: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Authenticate a player"""
        try:
            player = self.player_service.authenticate_player(name, session_id, ip_address)
            if not player:
                raise AuthenticationError("Invalid player name")
            
            return {
                "success": True,
                "data": player.get_summary(),
                "message": f"Player '{name}' authenticated successfully"
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_player(self, player_id: str) -> Dict[str, Any]:
        """Get player information"""
        try:
            player = self.player_service.get_player(player_id)
            if not player:
                return {
                    "success": False,
                    "error": "Player not found"
                }
            
            return {
                "success": True,
                "data": player.get_summary()
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_player_by_name(self, name: str) -> Dict[str, Any]:
        """Get player by name"""
        try:
            player = self.player_service.get_player_by_name(name)
            if not player:
                return {
                    "success": False,
                    "error": "Player not found"
                }
            
            return {
                "success": True,
                "data": player.get_summary()
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def logout_player(self, player_name: str) -> Dict[str, Any]:
        """Logout a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                return {
                    "success": False,
                    "error": "Player not found"
                }
            
            self.player_service.logout_player(player)
            return {
                "success": True,
                "message": f"Player '{player_name}' logged out successfully"
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    # Command Execution API
    
    def execute_command(self, player_name: str, command_line: str) -> Dict[str, Any]:
        """Execute a command for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            # Check passive mining before command execution
            self.player_service.check_passive_mining(player)
            
            result = self.command_service.execute_command(player, command_line)
            
            # Save player state after command
            self.player_service.repository.save(player)
            
            response_data = {
                "success": result.success,
                "output": result.output,
                "error": result.error if not result.success else None,
                "execution_time_ms": result.execution_time_ms,
                "data": result.data
            }

            if command_line.startswith("cat "):
                response_data["data"] = {
                    "type": "file_content",
                    "content": result.output
                }

            return response_data
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_available_commands(self, player_name: str) -> Dict[str, Any]:
        """Get available commands for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            commands = self.command_service.get_available_commands(player)
            
            return {
                "success": True,
                "data": commands
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_command_help(self, command_name: str = None) -> Dict[str, Any]:
        """Get command help"""
        try:
            help_text = self.command_service.get_command_help(command_name)
            return {
                "success": True,
                "data": help_text
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    # Mission Management API
    
    def get_available_missions(self, player_name: str) -> Dict[str, Any]:
        """Get available missions for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            missions = self.mission_service.get_available_missions(player)
            mission_data = [mission.get_progress_summary() for mission in missions]
            
            return {
                "success": True,
                "data": mission_data
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_active_missions(self, player_name: str) -> Dict[str, Any]:
        """Get active missions for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            missions = self.mission_service.get_active_missions(player)
            mission_data = [mission.get_progress_summary() for mission in missions]
            
            return {
                "success": True,
                "data": mission_data
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def start_mission(self, player_name: str, mission_id: str) -> Dict[str, Any]:
        """Start a mission for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            success, message = self.mission_service.start_mission(player, mission_id)
            
            if success:
                # Save player state
                self.player_service.repository.save(player)
            
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
    
    def abandon_mission(self, player_name: str, mission_id: str) -> Dict[str, Any]:
        """Abandon a mission for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            success, message = self.mission_service.abandon_mission(player, mission_id)
            
            if success:
                # Save player state
                self.player_service.repository.save(player)
            
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
    
    # Hardware Management API
    
    def upgrade_hardware(self, player_name: str, component: str) -> Dict[str, Any]:
        """Upgrade player hardware"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            success, message = self.player_service.upgrade_hardware(player, component)
            
            return {
                "success": success,
                "message": message,
                "data": player.virtual_computer.get_summary() if success else None
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_hardware_info(self, player_name: str) -> Dict[str, Any]:
        """Get player hardware information"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            hardware_info = player.virtual_computer.get_all_components_info()
            
            return {
                "success": True,
                "data": hardware_info
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    # Game State API
    
    def start_passive_mining(self, player_name: str, duration_hours: int) -> Dict[str, Any]:
        """Start passive mining for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            success = self.player_service.start_passive_mining(player, duration_hours)
            
            return {
                "success": success,
                "message": f"Passive mining started for {duration_hours} hours" if success else "Failed to start passive mining"
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def check_passive_mining(self, player_name: str) -> Dict[str, Any]:
        """Check passive mining status for a player"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                raise AuthenticationError("Player not found")
            
            credits = self.player_service.check_passive_mining(player)
            
            if credits:
                return {
                    "success": True,
                    "message": f"Passive mining completed! Earned {credits} credits.",
                    "data": {"credits_earned": credits}
                }
            else:
                time_remaining = player.virtual_computer.get_passive_mining_time_remaining()
                if time_remaining:
                    return {
                        "success": True,
                        "message": f"Passive mining in progress. Time remaining: {time_remaining}",
                        "data": {"time_remaining_seconds": time_remaining.total_seconds()}
                    }
                else:
                    return {
                        "success": True,
                        "message": "No passive mining in progress"
                    }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_leaderboard(self, category: str = "level", limit: int = 10) -> Dict[str, Any]:
        """Get player leaderboard"""
        try:
            leaderboard = self.player_service.get_leaderboard(limit, category)
            
            return {
                "success": True,
                "data": leaderboard
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def get_pvp_state(self) -> Dict[str, Any]:
        """Get PvP state"""
        online_players = self.player_repository.get_online_players()

        team_a = [{"name": p.name, "status": "Online" if p.is_online else "Offline"} for p in online_players if p.name.startswith("Player A")]
        team_b = [{"name": p.name, "status": "Online" if p.is_online else "Offline"} for p in online_players if p.name.startswith("Player B")]

        return {
            "success": True,
            "data": {
                "team_a": team_a,
                "team_b": team_b
            }
        }

    def get_player_state(self, player_name: str) -> Dict[str, Any]:
        """Get player state"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                return {
                    "success": False,
                    "error": "Player not found"
                }

            active_missions = self.mission_service.get_active_missions(player)

            return {
                "success": True,
                "data": {
                    "player": player.get_summary(),
                    "active_missions": [mission.to_dict() for mission in active_missions]
                }
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }

    def get_server_statistics(self) -> Dict[str, Any]:
        """Get server statistics"""
        try:
            stats = {
                "total_players": self.player_repository.count(),
                "online_players": self.player_repository.count_online(),
                "total_missions": self.mission_repository.count(),
                "mission_statistics": self.mission_repository.get_mission_statistics()
            }
            
            return {
                "success": True,
                "data": stats
            }
        except NexusException as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    # Utility Methods
    
    def validate_player_session(self, player_name: str, session_id: str) -> bool:
        """Validate a player session"""
        try:
            player = self.player_service.get_player_by_name(player_name)
            if not player:
                return False
            return player.session_id == session_id and player.is_online
        except:
            return False
    
    def cleanup_old_data(self):
        """Cleanup old data"""
        try:
            # Cleanup old sessions (24 hours)
            self.player_repository.cleanup_old_sessions(24)
            
            # Cleanup old missions (30 days)
            self.mission_repository.cleanup_old_missions(30)
            
            self.logger.info("Completed data cleanup")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def shutdown(self):
        """Shutdown the game API"""
        self.logger.info("Shutting down Game API")
        # Cleanup and close resources as needed