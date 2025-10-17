"""
Player data model
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from .virtual_computer import VirtualComputer
from ..core.events import Event, PlayerEvents

@dataclass
class PlayerStats:
    """Player statistics"""
    level: int = 1
    experience: int = 0
    credits: int = 0
    total_commands_executed: int = 0
    total_scripts_executed: int = 0
    total_missions_completed: int = 0
    playtime_minutes: int = 0
    
    def get_required_xp_for_next_level(self) -> int:
        """Calculate XP required for next level"""
        return self.level * 100
    
    def can_level_up(self) -> bool:
        """Check if player can level up"""
        return self.experience >= self.get_required_xp_for_next_level()

@dataclass
class KnowledgeMap:
    """Player's knowledge map (K-Map) for commands and concepts"""
    integrated_commands: List[str] = field(default_factory=lambda: ["set", "ls", "cat", "print"])
    unlocked_commands: List[str] = field(default_factory=list)
    locked_commands: List[str] = field(default_factory=lambda: [
        "scan", "run", "hashcrack", "pivot", "thread spawn", "raw", "edit"
    ])
    knowledge_fragments: Dict[str, int] = field(default_factory=dict)  # fragment_id -> count
    
    def is_command_available(self, command: str) -> bool:
        """Check if command is available to player"""
        return command in self.integrated_commands or command in self.unlocked_commands
    
    def unlock_command(self, command: str) -> bool:
        """Unlock a command if it's locked"""
        if command in self.locked_commands:
            self.locked_commands.remove(command)
            self.unlocked_commands.append(command)
            return True
        return False
    
    def integrate_command(self, command: str) -> bool:
        """Integrate an unlocked command"""
        if command in self.unlocked_commands:
            self.unlocked_commands.remove(command)
            self.integrated_commands.append(command)
            return True
        return False

class Player:
    """Main player class"""
    
    def __init__(self, name: str, is_vip: bool = False, session_id: str = None):
        self.id: Optional[str] = None  # Set by repository
        self.name = name
        self.is_vip = is_vip
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_login = datetime.now()
        self.is_online = False
        
        # Core components
        self.stats = PlayerStats()
        self.virtual_computer = VirtualComputer()
        self.knowledge_map = KnowledgeMap()
        
        # Game state
        self.active_missions: List[str] = []
        self.completed_missions: List[str] = []
        self.inventory: Dict[str, int] = {}
        self.settings: Dict[str, str] = {
            "theme": "default",
            "prompt_format": "{user}@nexus-root> "
        }
    
    def update_experience(self, amount: int, event_bus=None) -> bool:
        """Update player experience and handle level ups"""
        old_level = self.stats.level
        self.stats.experience += amount
        
        leveled_up = False
        while self.stats.can_level_up():
            self.stats.experience -= self.stats.get_required_xp_for_next_level()
            self.stats.level += 1
            leveled_up = True
        
        if leveled_up and event_bus:
            event_bus.publish(Event(
                PlayerEvents.PLAYER_LEVEL_UP,
                {
                    "player_id": self.id,
                    "player_name": self.name,
                    "old_level": old_level,
                    "new_level": self.stats.level,
                    "xp_gained": amount
                },
                source="player"
            ))
        
        return leveled_up
    
    def update_credits(self, amount: int, event_bus=None) -> bool:
        """Update player credits"""
        if self.stats.credits + amount < 0:
            return False
        
        old_credits = self.stats.credits
        self.stats.credits += amount
        
        if event_bus:
            event_bus.publish(Event(
                PlayerEvents.PLAYER_CREDITS_CHANGED,
                {
                    "player_id": self.id,
                    "player_name": self.name,
                    "old_credits": old_credits,
                    "new_credits": self.stats.credits,
                    "change": amount
                },
                source="player"
            ))
        
        return True
    
    def can_afford(self, cost: int) -> bool:
        """Check if player can afford something"""
        return self.stats.credits >= cost
    
    def login(self, event_bus=None):
        """Handle player login"""
        self.is_online = True
        self.last_login = datetime.now()
        
        if event_bus:
            event_bus.publish(Event(
                PlayerEvents.PLAYER_LOGGED_IN,
                {
                    "player_id": self.id,
                    "player_name": self.name,
                    "login_time": self.last_login.isoformat()
                },
                source="player"
            ))
    
    def logout(self, event_bus=None):
        """Handle player logout"""
        self.is_online = False
        
        if event_bus:
            event_bus.publish(Event(
                PlayerEvents.PLAYER_LOGGED_OUT,
                {
                    "player_id": self.id,
                    "player_name": self.name,
                    "logout_time": datetime.now().isoformat()
                },
                source="player"
            ))
    
    def get_summary(self) -> Dict[str, any]:
        """Get player summary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.stats.level,
            "experience": self.stats.experience,
            "credits": self.stats.credits,
            "is_vip": self.is_vip,
            "is_online": self.is_online,
            "virtual_computer": self.virtual_computer.get_summary(),
            "theme": self.settings.get("theme", "default")
        }
    
    def to_dict(self) -> Dict[str, any]:
        """Convert player to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "is_vip": self.is_vip,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat(),
            "is_online": self.is_online,
            "stats": {
                "level": self.stats.level,
                "experience": self.stats.experience,
                "credits": self.stats.credits,
                "total_commands_executed": self.stats.total_commands_executed,
                "total_scripts_executed": self.stats.total_scripts_executed,
                "total_missions_completed": self.stats.total_missions_completed,
                "playtime_minutes": self.stats.playtime_minutes
            },
            "virtual_computer": self.virtual_computer.to_dict(),
            "knowledge_map": {
                "integrated_commands": self.knowledge_map.integrated_commands,
                "unlocked_commands": self.knowledge_map.unlocked_commands,
                "locked_commands": self.knowledge_map.locked_commands,
                "knowledge_fragments": self.knowledge_map.knowledge_fragments
            },
            "active_missions": self.active_missions,
            "completed_missions": self.completed_missions,
            "inventory": self.inventory,
            "settings": self.settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Player":
        """Create player from dictionary"""
        player = cls(
            name=data["name"],
            is_vip=data.get("is_vip", False),
            session_id=data.get("session_id")
        )
        
        player.id = data.get("id")
        if data.get("created_at"):
            player.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_login"):
            player.last_login = datetime.fromisoformat(data["last_login"])
        player.is_online = data.get("is_online", False)
        
        # Load stats
        if "stats" in data:
            stats_data = data["stats"]
            player.stats.level = stats_data.get("level", 1)
            player.stats.experience = stats_data.get("experience", 0)
            player.stats.credits = stats_data.get("credits", 0)
            player.stats.total_commands_executed = stats_data.get("total_commands_executed", 0)
            player.stats.total_scripts_executed = stats_data.get("total_scripts_executed", 0)
            player.stats.total_missions_completed = stats_data.get("total_missions_completed", 0)
            player.stats.playtime_minutes = stats_data.get("playtime_minutes", 0)
        
        # Load virtual computer
        if "virtual_computer" in data:
            player.virtual_computer = VirtualComputer.from_dict(data["virtual_computer"])
        
        # Load knowledge map
        if "knowledge_map" in data:
            kmap_data = data["knowledge_map"]
            player.knowledge_map.integrated_commands = kmap_data.get("integrated_commands", ["set", "ls", "cat", "print"])
            player.knowledge_map.unlocked_commands = kmap_data.get("unlocked_commands", [])
            player.knowledge_map.locked_commands = kmap_data.get("locked_commands", ["scan", "run", "hashcrack", "pivot", "thread spawn", "raw", "edit"])
            player.knowledge_map.knowledge_fragments = kmap_data.get("knowledge_fragments", {})
        
        # Load other data
        player.active_missions = data.get("active_missions", [])
        player.completed_missions = data.get("completed_missions", [])
        player.inventory = data.get("inventory", {})
        player.settings = data.get("settings", {"theme": "default", "prompt_format": "{user}@nexus-root> "})
        
        return player