from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..models.player import Player

class CommandResult:
    """Result of command execution"""
    def __init__(self, success: bool, output: str = "", error: str = "", data: Dict[str, Any] = None, animation_type: str = "TEXT_ONLY"):
        self.success = success
        self.output = output
        self.error = error
        self.data = data or {}
        self.execution_time_ms: float = 0
        self.animation_type = animation_type

class Command(ABC):
    """Abstract base class for commands"""

    def __init__(self, name: str, description: str, syntax: str):
        self.name = name
        self.description = description
        self.syntax = syntax
        self.requires_vip = False
        self.min_level = 1
        self.resource_cost = 0
        self.heat_cost = 5.0 # Base heat cost

    @abstractmethod
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        """Execute the command"""
        pass

    def can_execute(self, player: Player) -> tuple[bool, str]:
        """Check if player can execute this command"""
        if not player.knowledge_map.is_command_available(self.name):
            return False, f"Command '{self.name}' is not available. Check your K-Map."

        if player.stats.level < self.min_level:
            return False, f"Command requires level {self.min_level}"

        if self.requires_vip and not player.is_vip:
            return False, f"Command '{self.name}' requires VIP access"

        if self.resource_cost > 0 and not player.can_afford(self.resource_cost):
            return False, f"Command costs {self.resource_cost} credits"

        return True, "OK"
