"""
Mission management service
"""

from typing import List, Optional, Dict, Any
from ..models.mission import Mission, MissionStatus, MissionType, MissionObjective, MissionReward
from ..models.player import Player
from ..core.events import EventBus, Event, GameEvents
from ..core.exceptions import ValidationError
from ..core.logger import NexusLogger

class MissionService:
    """Service for managing missions"""
    
    def __init__(self, mission_repository, event_bus: EventBus = None):
        self.repository = mission_repository
        self.event_bus = event_bus or EventBus()
        self.logger = NexusLogger.get_logger("mission_service")
        
        # Initialize default missions if repository is empty
        self._initialize_default_missions()
    
    def _initialize_default_missions(self):
        """Initialize default tutorial and starter missions"""
        if self.repository.count() == 0:
            self._create_tutorial_missions()
            self.logger.info("Initialized default missions")
    
    def _create_tutorial_missions(self):
        """Create tutorial missions"""
        # Tutorial Mission 1: File System Basics
        mission1 = Mission(
            mission_id="tutorial_001",
            name="Terminal Basics",
            description="Learn basic file system navigation",
            mission_type=MissionType.TUTORIAL,
            reward=MissionReward(
                experience=50,
                credits=25,
                unlocked_commands=["ls"]
            ),
            level_requirement=1
        )
        mission1.add_objective(MissionObjective("ls_files", "Use 'ls' command to list files", 1))
        mission1.add_objective(MissionObjective("cat_file", "Use 'cat' to read a file", 1))
        mission1.status = MissionStatus.AVAILABLE
        
        # Tutorial Mission 2: Network Discovery
        mission2 = Mission(
            mission_id="tutorial_002",
            name="Network Discovery",
            description="Learn network scanning basics",
            mission_type=MissionType.TUTORIAL,
            reward=MissionReward(
                experience=100,
                credits=50,
                unlocked_commands=["scan"]
            ),
            prerequisites=["tutorial_001"],
            level_requirement=2
        )
        mission2.add_objective(MissionObjective("scan_target", "Scan a network target", 1))
        mission2.add_objective(MissionObjective("identify_services", "Identify running services", 3))
        
        # Tutorial Mission 3: Password Cracking
        mission3 = Mission(
            mission_id="tutorial_003",
            name="Hash Cracking",
            description="Learn password hash cracking",
            mission_type=MissionType.TUTORIAL,
            reward=MissionReward(
                experience=150,
                credits=100,
                unlocked_commands=["hashcrack"]
            ),
            prerequisites=["tutorial_002"],
            level_requirement=3
        )
        mission3.add_objective(MissionObjective("crack_hash", "Crack a password hash", 1))
        
        # Save missions
        for mission in [mission1, mission2, mission3]:
            self.repository.save(mission)
    
    def create_mission(
        self,
        mission_id: str,
        name: str,
        description: str,
        mission_type: MissionType = MissionType.MAIN,
        reward: MissionReward = None,
        **kwargs
    ) -> Mission:
        """Create a new mission"""
        if self.repository.find_by_id(mission_id):
            raise ValidationError(f"Mission with ID '{mission_id}' already exists")
        
        mission = Mission(
            mission_id=mission_id,
            name=name,
            description=description,
            mission_type=mission_type,
            reward=reward or MissionReward(),
            **kwargs
        )
        
        saved_mission = self.repository.save(mission)
        self.logger.info(f"Created mission: {mission_id}")
        
        return saved_mission
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get mission by ID"""
        return self.repository.find_by_id(mission_id)
    
    def get_available_missions(self, player: Player) -> List[Mission]:
        """Get missions available to player"""
        all_missions = self.repository.find_all()
        available = []
        
        for mission in all_missions:
            # Skip completed missions
            if mission.id in player.completed_missions:
                continue
            
            # Check if mission is available
            if mission.status == MissionStatus.LOCKED:
                # Check if prerequisites are met
                prereqs_met = all(prereq in player.completed_missions for prereq in mission.prerequisites)
                level_met = player.stats.level >= mission.level_requirement
                
                if prereqs_met and level_met:
                    mission.status = MissionStatus.AVAILABLE
                    self.repository.save(mission)
            
            if mission.status == MissionStatus.AVAILABLE:
                available.append(mission)
        
        return available
    
    def get_active_missions(self, player: Player) -> List[Mission]:
        """Get active missions for player"""
        return self.repository.find_by_player_and_status(player.id, MissionStatus.IN_PROGRESS)
    
    def start_mission(self, player: Player, mission_id: str) -> tuple[bool, str]:
        """Start a mission for player"""
        mission = self.get_mission(mission_id)
        if not mission:
            return False, "Mission not found"
        
        # Check if already completed
        if mission_id in player.completed_missions:
            return False, "Mission already completed"
        
        # Check if already active
        active_missions = self.get_active_missions(player)
        if any(m.id == mission_id for m in active_missions):
            return False, "Mission already in progress"
        
        # Try to start mission
        success = mission.start(player)
        if not success:
            can_start, reason = mission.can_start(player)
            return False, reason
        
        # Add to player's active missions
        if mission_id not in player.active_missions:
            player.active_missions.append(mission_id)
        
        # Save changes
        self.repository.save(mission)
        
        # Publish event
        self.event_bus.publish(Event(
            "game.mission_started",
            {
                "player_id": player.id,
                "player_name": player.name,
                "mission_id": mission_id,
                "mission_name": mission.name
            },
            source="mission_service"
        ))
        
        self.logger.info(f"Player {player.name} started mission: {mission_id}")
        return True, f"Mission '{mission.name}' started!"
    
    def update_mission_progress(
        self,
        player: Player,
        mission_id: str,
        objective_id: str,
        amount: int = 1
    ) -> bool:
        """Update mission objective progress"""
        mission = self.get_mission(mission_id)
        if not mission or mission.player_id != player.id:
            return False
        
        if mission.status != MissionStatus.IN_PROGRESS:
            return False
        
        # Update objective
        objective_completed = mission.update_objective_progress(objective_id, amount)
        
        # Check mission completion
        mission_completed = mission.check_completion(player)
        
        if mission_completed:
            # Remove from active missions
            if mission_id in player.active_missions:
                player.active_missions.remove(mission_id)
            
            # Publish completion event
            self.event_bus.publish(Event(
                GameEvents.MISSION_COMPLETED,
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "mission_id": mission_id,
                    "mission_name": mission.name,
                    "experience_gained": mission.reward.experience,
                    "credits_gained": mission.reward.credits
                },
                source="mission_service"
            ))
            
            self.logger.info(f"Player {player.name} completed mission: {mission_id}")
        
        # Save mission
        self.repository.save(mission)
        
        return True
    
    def abandon_mission(self, player: Player, mission_id: str) -> tuple[bool, str]:
        """Abandon a mission"""
        mission = self.get_mission(mission_id)
        if not mission:
            return False, "Mission not found"
        
        if mission.player_id != player.id:
            return False, "Not your mission"
        
        if mission.status != MissionStatus.IN_PROGRESS:
            return False, "Mission not in progress"
        
        # Reset mission
        mission.status = MissionStatus.AVAILABLE
        mission.player_id = None
        mission.started_at = None
        
        # Reset objectives
        for objective in mission.objectives:
            objective.current_count = 0
            objective.is_completed = False
        
        # Remove from player's active missions
        if mission_id in player.active_missions:
            player.active_missions.remove(mission_id)
        
        self.repository.save(mission)
        
        self.logger.info(f"Player {player.name} abandoned mission: {mission_id}")
        return True, f"Mission '{mission.name}' abandoned"
    
    def get_mission_progress(self, player: Player, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed mission progress"""
        mission = self.get_mission(mission_id)
        if not mission:
            return None
        
        return mission.get_progress_summary()
    
    def handle_command_execution(self, player: Player, command: str, success: bool, data: Dict[str, Any] = None):
        """Handle command execution for mission progress"""
        active_missions = self.get_active_missions(player)
        data = data or {}
        
        for mission in active_missions:
            # Check objectives that might be completed by this command
            for objective in mission.objectives:
                if objective.is_completed:
                    continue
                
                # Simple objective matching based on command and objective ID
                objective_updated = False
                
                if command == "ls" and objective.id == "ls_files":
                    objective_updated = True
                elif command == "cat" and objective.id == "cat_file":
                    objective_updated = True
                elif command == "scan" and objective.id == "scan_target":
                    objective_updated = True
                elif command == "scan" and objective.id == "identify_services" and success:
                    services_found = len(data.get("services", []))
                    objective_updated = services_found > 0
                elif command == "hashcrack" and objective.id == "crack_hash" and success:
                    objective_updated = True
                
                if objective_updated:
                    self.update_mission_progress(player, mission.id, objective.id)
    
    def get_mission_templates(self) -> List[Dict[str, Any]]:
        """Get available mission templates for admin use"""
        return [
            {
                "id": "recon_basic",
                "name": "Basic Reconnaissance",
                "description": "Perform basic network reconnaissance",
                "type": "main",
                "objectives": [
                    {"id": "scan_network", "desc": "Scan target network", "count": 1},
                    {"id": "identify_os", "desc": "Identify target OS", "count": 1}
                ],
                "reward": {"xp": 100, "credits": 50}
            },
            {
                "id": "exploit_web",
                "name": "Web Application Testing",
                "description": "Test web application for vulnerabilities",
                "type": "main",
                "objectives": [
                    {"id": "scan_web", "desc": "Scan web application", "count": 1},
                    {"id": "find_vuln", "desc": "Find vulnerabilities", "count": 3}
                ],
                "reward": {"xp": 200, "credits": 100}
            }
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get mission statistics"""
        total_missions = self.repository.count()
        completed_missions = self.repository.count_by_status(MissionStatus.COMPLETED)
        active_missions = self.repository.count_by_status(MissionStatus.IN_PROGRESS)
        
        return {
            "total_missions": total_missions,
            "completed_missions": completed_missions,
            "active_missions": active_missions,
            "completion_rate": (completed_missions / total_missions * 100) if total_missions > 0 else 0
        }