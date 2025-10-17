"""
Player service layer
"""

import sqlite3
from typing import Optional, List, Dict, Any
from ..models.player import Player
from ..core.events import EventBus, Event, PlayerEvents
from ..core.exceptions import ValidationError, InsufficientCreditsError, AuthenticationError
from ..core.logger import NexusLogger

class PlayerService:
    """Service for managing player operations"""
    
    def __init__(self, player_repository, event_bus: EventBus = None):
        self.repository = player_repository
        self.event_bus = event_bus or EventBus()
        self.logger = NexusLogger.get_logger("player_service")
    
    def create_player(self, name: str, is_vip: bool = False, session_id: str = None) -> Player:
        """Create a new player"""
        # Validate name
        if not name or len(name) < 2 or len(name) > 20:
            raise ValidationError("Player name must be 2-20 characters")
        
        if not name.replace("_", "").replace("-", "").isalnum():
            raise ValidationError("Player name can only contain letters, numbers, hyphens, and underscores")
        
        # Check if name is taken
        existing_player = self.repository.find_by_name(name)
        if existing_player:
            raise ValidationError(f"Player name '{name}' is already taken")
        
        # Create player
        player = Player(name=name, is_vip=is_vip, session_id=session_id)
        saved_player = self.repository.save(player)
        
        # Publish event
        self.event_bus.publish(Event(
            PlayerEvents.PLAYER_CREATED,
            {
                "player_id": saved_player.id,
                "player_name": saved_player.name,
                "is_vip": saved_player.is_vip
            },
            source="player_service"
        ))
        
        self.logger.info(f"Created new player: {name} (VIP: {is_vip})")
        return saved_player
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        return self.repository.find_by_id(player_id)
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Get player by name"""
        return self.repository.find_by_name(name)
    
    def authenticate_player(self, name: str, session_id: str = None, ip_address: str = None) -> Optional[Player]:
        """Authenticate player login"""
        if self.is_ip_banned(ip_address):
            raise AuthenticationError("Your IP address has been banned.")

        player = self.repository.find_by_name(name)
        if not player:
            return None
        
        # Update session
        if session_id:
            player.session_id = session_id
            self.repository.save(player)
        
        # Handle login
        player.login(self.event_bus)
        player.is_online = True
        self.repository.save(player)
        self.logger.info(f"Player authenticated: {name}")
        
        return player

    def is_ip_banned(self, ip_address: str) -> bool:
        """Check if an IP address is banned"""
        if not ip_address:
            return False

        try:
            with sqlite3.connect(self.repository.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM banned_ips WHERE ip_address = ?",
                    (ip_address,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to check if IP address {ip_address} is banned: {e}")
            return False

    def lock_cpu(self, player, duration_seconds: int):
        """Lock a player's CPU for a specified duration"""
        from datetime import datetime, timedelta

        player.cpu_locked_until = datetime.now() + timedelta(seconds=duration_seconds)
        self.repository.save(player)
        self.logger.info(f"Locked CPU for player {player.name} for {duration_seconds} seconds.")
    
    def logout_player(self, player: Player):
        """Handle player logout"""
        player.logout(self.event_bus)
        self.repository.save(player)
        self.logger.info(f"Player logged out: {player.name}")
    
    def update_experience(self, player: Player, amount: int) -> bool:
        """Update player experience"""
        if amount < 0:
            raise ValidationError("Experience amount cannot be negative")
        
        leveled_up = player.update_experience(amount, self.event_bus)
        self.repository.save(player)
        
        self.logger.info(f"Updated experience for {player.name}: +{amount} XP (Level: {player.stats.level})")
        return leveled_up
    
    def update_credits(self, player: Player, amount: int, reason: str = "") -> bool:
        """Update player credits"""
        if amount < 0 and not player.can_afford(abs(amount)):
            raise InsufficientCreditsError(f"Player has {player.stats.credits} credits, needs {abs(amount)}")
        
        success = player.update_credits(amount, self.event_bus)
        if success:
            self.repository.save(player)
            action = "gained" if amount > 0 else "spent"
            self.logger.info(f"Player {player.name} {action} {abs(amount)} credits. Reason: {reason}")
        
        return success
    
    def upgrade_hardware(self, player: Player, component: str) -> tuple[bool, str]:
        """Upgrade player hardware"""
        success, cost = player.virtual_computer.upgrade_component(component)
        
        if not success:
            if cost == 0:
                return False, f"{component.upper()} is already at maximum tier"
            else:
                return False, f"Failed to upgrade {component}"
        
        if not player.can_afford(cost):
            # Rollback upgrade
            getattr(player.virtual_computer, component).tier -= 1
            raise InsufficientCreditsError(f"Upgrade costs {cost} credits, player has {player.stats.credits}")
        
        # Charge credits
        player.update_credits(-cost, self.event_bus)
        
        # Publish event
        self.event_bus.publish(Event(
            PlayerEvents.PLAYER_UPGRADED_HARDWARE,
            {
                "player_id": player.id,
                "player_name": player.name,
                "component": component,
                "new_tier": getattr(player.virtual_computer, component).tier,
                "cost": cost
            },
            source="player_service"
        ))
        
        self.repository.save(player)
        
        new_tier = getattr(player.virtual_computer, component).tier
        self.logger.info(f"Player {player.name} upgraded {component} to tier {new_tier} for {cost} credits")
        
        return True, f"Successfully upgraded {component.upper()} to tier {new_tier}"
    
    def unlock_command(self, player: Player, command: str) -> bool:
        """Unlock a command for the player"""
        success = player.knowledge_map.unlock_command(command)
        if success:
            self.repository.save(player)
            self.logger.info(f"Unlocked command '{command}' for player {player.name}")
        
        return success
    
    def check_passive_mining(self, player: Player) -> Optional[int]:
        """Check and collect passive mining rewards"""
        credits = player.virtual_computer.check_passive_mining()
        
        if credits:
            self.update_credits(player, credits, "passive mining completion")
            self.event_bus.publish(Event(
                "game.passive_mining_completed",
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "credits_earned": credits
                },
                source="player_service"
            ))
            
        return credits
    
    def start_passive_mining(self, player: Player, duration_hours: int) -> bool:
        """Start passive mining for the player"""
        if duration_hours <= 0 or duration_hours > 24:
            raise ValidationError("Mining duration must be between 1 and 24 hours")
        
        success = player.virtual_computer.start_passive_mining(duration_hours)
        
        if success:
            self.repository.save(player)
            self.event_bus.publish(Event(
                "game.passive_mining_started",
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "duration_hours": duration_hours
                },
                source="player_service"
            ))
            self.logger.info(f"Started passive mining for {player.name}: {duration_hours} hours")
        
        return success
    
    def update_settings(self, player: Player, settings: Dict[str, str]) -> bool:
        """Update player settings"""
        valid_settings = ["theme", "prompt_format"]
        
        for key, value in settings.items():
            if key not in valid_settings:
                raise ValidationError(f"Invalid setting: {key}")
            
            player.settings[key] = value
        
        self.repository.save(player)
        self.logger.info(f"Updated settings for player {player.name}: {settings}")
        
        return True
    
    def get_leaderboard(self, limit: int = 10, category: str = "level") -> List[Dict[str, Any]]:
        """Get player leaderboard"""
        valid_categories = ["level", "credits", "missions"]
        
        if category not in valid_categories:
            raise ValidationError(f"Invalid leaderboard category: {category}")
        
        players = self.repository.get_leaderboard(category, limit)
        
        return [
            {
                "rank": i + 1,
                "name": player.name,
                "level": player.stats.level,
                "credits": player.stats.credits,
                "missions_completed": player.stats.total_missions_completed,
                "is_vip": player.is_vip
            }
            for i, player in enumerate(players)
        ]