"""
Mission data model
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

class MissionStatus(Enum):
    """Mission status enumeration"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class MissionType(Enum):
    """Mission type enumeration"""
    TUTORIAL = "tutorial"
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    WEEKLY = "weekly"
    SPECIAL = "special"
    PVP = "pvp"

@dataclass
class MissionReward:
    """Mission reward structure"""
    experience: int = 0
    credits: int = 0
    items: Dict[str, int] = field(default_factory=dict)
    unlocked_commands: List[str] = field(default_factory=list)
    knowledge_fragments: Dict[str, int] = field(default_factory=dict)

@dataclass
class MissionObjective:
    """Individual mission objective"""
    id: str
    description: str
    required_count: int = 1
    current_count: int = 0
    is_completed: bool = False
    
    def update_progress(self, amount: int = 1) -> bool:
        """Update objective progress"""
        self.current_count = min(self.current_count + amount, self.required_count)
        self.is_completed = self.current_count >= self.required_count
        return self.is_completed

class MissionValidator(ABC):
    """Abstract base class for mission validation"""
    
    @abstractmethod
    def validate(self, player, context: Dict[str, Any]) -> bool:
        """Validate mission completion criteria"""
        pass

class Mission:
    """Main mission class"""
    
    def __init__(
        self,
        mission_id: str,
        name: str,
        description: str,
        mission_type: MissionType = MissionType.MAIN,
        reward: MissionReward = None,
        prerequisites: List[str] = None,
        level_requirement: int = 1,
        time_limit_hours: Optional[int] = None
    ):
        self.id = mission_id
        self.name = name
        self.description = description
        self.type = mission_type
        self.reward = reward or MissionReward()
        self.prerequisites = prerequisites or []
        self.level_requirement = level_requirement
        self.time_limit_hours = time_limit_hours
        
        # Mission state
        self.status = MissionStatus.LOCKED
        self.objectives: List[MissionObjective] = []
        self.validator: Optional[MissionValidator] = None
        
        # Tracking
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.player_id: Optional[str] = None
        
        # Metadata
        self.difficulty: str = "normal"  # easy, normal, hard, expert
        self.category: str = "general"   # reconnaissance, exploitation, etc.
        self.tags: List[str] = []
    
    def add_objective(self, objective: MissionObjective):
        """Add an objective to the mission"""
        self.objectives.append(objective)
    
    def can_start(self, player) -> tuple[bool, str]:
        """Check if player can start this mission"""
        if self.status != MissionStatus.AVAILABLE:
            return False, f"Mission is {self.status.value}"
        
        if player.stats.level < self.level_requirement:
            return False, f"Requires level {self.level_requirement}"
        
        # Check prerequisites
        for prereq in self.prerequisites:
            if prereq not in player.completed_missions:
                return False, f"Missing prerequisite: {prereq}"
        
        return True, "OK"
    
    def start(self, player) -> bool:
        """Start the mission for a player"""
        can_start, reason = self.can_start(player)
        if not can_start:
            return False
        
        self.status = MissionStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.player_id = player.id
        
        return True
    
    def update_objective_progress(self, objective_id: str, amount: int = 1) -> bool:
        """Update progress for a specific objective"""
        for objective in self.objectives:
            if objective.id == objective_id:
                return objective.update_progress(amount)
        return False
    
    def check_completion(self, player, context: Dict[str, Any] = None) -> bool:
        """Check if mission is completed"""
        if self.status != MissionStatus.IN_PROGRESS:
            return False
        
        # Check all objectives
        all_objectives_complete = all(obj.is_completed for obj in self.objectives)
        
        # Use custom validator if available
        custom_validation = True
        if self.validator:
            custom_validation = self.validator.validate(player, context or {})
        
        if all_objectives_complete and custom_validation:
            self.complete(player)
            return True
        
        return False
    
    def complete(self, player):
        """Complete the mission"""
        self.status = MissionStatus.COMPLETED
        self.completed_at = datetime.now()
        
        # Award rewards
        player.update_experience(self.reward.experience)
        player.update_credits(self.reward.credits)
        
        # Unlock commands
        for command in self.reward.unlocked_commands:
            player.knowledge_map.unlock_command(command)
        
        # Add items to inventory
        for item, quantity in self.reward.items.items():
            player.inventory[item] = player.inventory.get(item, 0) + quantity
        
        # Add knowledge fragments
        for fragment, count in self.reward.knowledge_fragments.items():
            player.knowledge_map.knowledge_fragments[fragment] = \
                player.knowledge_map.knowledge_fragments.get(fragment, 0) + count
        
        # Track completion
        if self.id not in player.completed_missions:
            player.completed_missions.append(self.id)
        
        player.stats.total_missions_completed += 1
    
    def fail(self, reason: str = ""):
        """Fail the mission"""
        self.status = MissionStatus.FAILED
        # Could implement penalties here
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get mission progress summary"""
        return {
            "mission_id": self.id,
            "name": self.name,
            "status": self.status.value,
            "type": self.type.value,
            "difficulty": self.difficulty,
            "objectives": [
                {
                    "id": obj.id,
                    "description": obj.description,
                    "progress": f"{obj.current_count}/{obj.required_count}",
                    "completed": obj.is_completed
                }
                for obj in self.objectives
            ],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mission to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "status": self.status.value,
            "difficulty": self.difficulty,
            "category": self.category,
            "tags": self.tags,
            "level_requirement": self.level_requirement,
            "time_limit_hours": self.time_limit_hours,
            "prerequisites": self.prerequisites,
            "reward": {
                "experience": self.reward.experience,
                "credits": self.reward.credits,
                "items": self.reward.items,
                "unlocked_commands": self.reward.unlocked_commands,
                "knowledge_fragments": self.reward.knowledge_fragments
            },
            "objectives": [
                {
                    "id": obj.id,
                    "description": obj.description,
                    "required_count": obj.required_count,
                    "current_count": obj.current_count,
                    "is_completed": obj.is_completed
                }
                for obj in self.objectives
            ],
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "player_id": self.player_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Mission":
        """Create mission from dictionary"""
        reward = MissionReward(
            experience=data.get("reward", {}).get("experience", 0),
            credits=data.get("reward", {}).get("credits", 0),
            items=data.get("reward", {}).get("items", {}),
            unlocked_commands=data.get("reward", {}).get("unlocked_commands", []),
            knowledge_fragments=data.get("reward", {}).get("knowledge_fragments", {})
        )
        
        mission = cls(
            mission_id=data["id"],
            name=data["name"],
            description=data["description"],
            mission_type=MissionType(data.get("type", "main")),
            reward=reward,
            prerequisites=data.get("prerequisites", []),
            level_requirement=data.get("level_requirement", 1),
            time_limit_hours=data.get("time_limit_hours")
        )
        
        mission.status = MissionStatus(data.get("status", "locked"))
        mission.difficulty = data.get("difficulty", "normal")
        mission.category = data.get("category", "general")
        mission.tags = data.get("tags", [])
        
        # Load objectives
        for obj_data in data.get("objectives", []):
            objective = MissionObjective(
                id=obj_data["id"],
                description=obj_data["description"],
                required_count=obj_data.get("required_count", 1),
                current_count=obj_data.get("current_count", 0),
                is_completed=obj_data.get("is_completed", False)
            )
            mission.add_objective(objective)
        
        # Load timestamps
        if data.get("created_at"):
            mission.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            mission.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            mission.completed_at = datetime.fromisoformat(data["completed_at"])
        
        mission.player_id = data.get("player_id")
        
        return mission