"""
Player service layer
"""

import sqlite3
from typing import Optional, List, Dict, Any
from ..models.player import Player
from ..models.item import Consumable
from ..models.blockchain import game_blockchain
from ..core.events import EventBus, Event, PlayerEvents
from ..core.exceptions import ValidationError, InsufficientCreditsError, AuthenticationError
from ..core.logger import NexusLogger

class PlayerService:
    """Service for managing player operations"""
    
    def __init__(self, player_repository, event_bus: EventBus = None):
        self.repository = player_repository
        self.event_bus = event_bus or EventBus()
        self.logger = NexusLogger.get_logger("player_service")
    
    # ... (previous methods omitted for brevity, assuming they are preserved if I use merge, but I am overwriting so I must include all)
    # Wait, I am overwriting. I need to include ALL methods.

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
        return self.repository.find_by_id(player_id)
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        return self.repository.find_by_name(name)
    
    def authenticate_player(self, name: str, session_id: str = None, ip_address: str = None) -> Optional[Player]:
        if self.is_ip_banned(ip_address):
            raise AuthenticationError("Your IP address has been banned.")

        player = self.repository.find_by_name(name)
        if not player:
            return None
        
        if session_id:
            player.session_id = session_id
            self.repository.save(player)
        
        player.login(self.event_bus)
        player.is_online = True
        self.repository.save(player)
        self.logger.info(f"Player authenticated: {name}")
        
        return player

    def is_ip_banned(self, ip_address: str) -> bool:
        if not ip_address:
            return False
        try:
            with sqlite3.connect(self.repository.db_path) as conn:
                cursor = conn.execute("SELECT 1 FROM banned_ips WHERE ip_address = ?", (ip_address,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to check if IP address {ip_address} is banned: {e}")
            return False

    def lock_cpu(self, player, duration_seconds: int):
        from datetime import datetime, timedelta
        player.cpu_locked_until = datetime.now() + timedelta(seconds=duration_seconds)
        self.repository.save(player)
        self.logger.info(f"Locked CPU for player {player.name} for {duration_seconds} seconds.")
    
    def logout_player(self, player: Player):
        player.logout(self.event_bus)
        self.repository.save(player)
        self.logger.info(f"Player logged out: {player.name}")
    
    def update_experience(self, player: Player, amount: int) -> bool:
        if amount < 0:
            raise ValidationError("Experience amount cannot be negative")
        leveled_up = player.update_experience(amount, self.event_bus)
        self.repository.save(player)
        self.logger.info(f"Updated experience for {player.name}: +{amount} XP (Level: {player.stats.level})")
        return leveled_up
    
    def update_credits(self, player: Player, amount: int, reason: str = "") -> bool:
        if amount < 0 and not player.can_afford(abs(amount)):
            raise InsufficientCreditsError(f"Player has {player.stats.credits} credits, needs {abs(amount)}")
        
        success = player.update_credits(amount, self.event_bus)
        if success:
            self.repository.save(player)
            action = "gained" if amount > 0 else "spent"
            self.logger.info(f"Player {player.name} {action} {abs(amount)} credits. Reason: {reason}")

            sender = "SYSTEM"
            recipient = player.wallet_address
            if amount < 0:
                sender = player.wallet_address
                recipient = "SYSTEM"

            game_blockchain.add_transaction(sender, recipient, abs(amount), memo=reason)
            game_blockchain.mine_pending_transactions("MINER_POOL")

        return success
    
    def upgrade_hardware(self, player: Player, component: str) -> tuple[bool, str]:
        # Legacy/Basic tier upgrade
        success, cost = player.virtual_computer.upgrade_component(component)
        
        if not success:
            if cost == 0:
                return False, f"{component.upper()} is already at maximum tier"
            else:
                return False, f"Failed to upgrade {component}"
        
        if not player.can_afford(cost):
            # Rollback logic for tiers
            if component == "cpu": player.virtual_computer.cpu_tier -= 1
            elif component == "ram": player.virtual_computer.ram_tier -= 1
            elif component == "nic": player.virtual_computer.nic_tier -= 1
            elif component == "ssd": player.virtual_computer.ssd_tier -= 1
            raise InsufficientCreditsError(f"Upgrade costs {cost} credits, player has {player.stats.credits}")
        
        self.update_credits(player, -cost, f"Upgrade {component}")
        
        new_tier = 0
        if component == "nic": new_tier = player.virtual_computer.nic_tier
        elif component == "ssd": new_tier = player.virtual_computer.ssd_tier
        elif component == "cpu": new_tier = player.virtual_computer.cpu_tier
        elif component == "ram": new_tier = player.virtual_computer.ram_tier

        self.event_bus.publish(Event(
            PlayerEvents.PLAYER_UPGRADED_HARDWARE,
            {
                "player_id": player.id,
                "player_name": player.name,
                "component": component,
                "new_tier": new_tier,
                "cost": cost
            },
            source="player_service"
        ))
        
        self.repository.save(player)
        self.logger.info(f"Player {player.name} upgraded {component} to tier {new_tier} for {cost} credits")
        return True, f"Successfully upgraded {component.upper()} to tier {new_tier}"
    
    def unlock_command(self, player: Player, command: str) -> bool:
        success = player.knowledge_map.unlock_command(command)
        if success:
            self.repository.save(player)
            self.logger.info(f"Unlocked command '{command}' for player {player.name}")
        return success
    
    def check_passive_mining(self, player: Player) -> Optional[int]:
        credits = player.virtual_computer.check_passive_mining()
        if credits:
            self.update_credits(player, credits, "passive mining completion")
            self.event_bus.publish(Event("game.passive_mining_completed", {"player_id": player.id, "credits_earned": credits}, source="player_service"))
        return credits
    
    def start_passive_mining(self, player: Player, duration_hours: int) -> bool:
        if duration_hours <= 0 or duration_hours > 24:
            raise ValidationError("Mining duration must be between 1 and 24 hours")
        success = player.virtual_computer.start_passive_mining(duration_hours)
        if success:
            self.repository.save(player)
            self.event_bus.publish(Event("game.passive_mining_started", {"player_id": player.id, "duration_hours": duration_hours}, source="player_service"))
            self.logger.info(f"Started passive mining for {player.name}: {duration_hours} hours")
        return success
    
    def update_settings(self, player: Player, settings: Dict[str, str]) -> bool:
        valid_settings = ["theme", "prompt_format"]
        for key, value in settings.items():
            if key not in valid_settings:
                raise ValidationError(f"Invalid setting: {key}")
            player.settings[key] = value
        self.repository.save(player)
        self.logger.info(f"Updated settings for player {player.name}: {settings}")
        return True
    
    def get_leaderboard(self, limit: int = 10, category: str = "level") -> List[Dict[str, Any]]:
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

    # --- Item & Inventory Methods ---

    def equip_item(self, player: Player, item_id: str, slot: str) -> tuple[bool, str]:
        """Equip an item from inventory"""
        if player.equip_item(item_id, slot):
            self.repository.save(player)
            self.logger.info(f"Player {player.name} equipped item {item_id} to {slot}")
            return True, f"Equipped item to {slot}."
        return False, "Failed to equip item. Check inventory or slot compatibility."

    def use_item(self, player: Player, item_id: str) -> tuple[bool, str]:
        """Use a consumable item"""
        item_to_use = None
        for item in player.inventory:
            if item.id == item_id:
                item_to_use = item
                break

        if not item_to_use:
            return False, "Item not found."

        if not isinstance(item_to_use, Consumable):
            return False, "Item is not usable."

        # Apply effects
        effect_msg = ""
        if item_to_use.effect == "restore_heat":
            player.virtual_computer.current_heat = max(0.0, player.virtual_computer.current_heat - item_to_use.effect_value)
            effect_msg = f"Cooled down system by {item_to_use.effect_value}."
        elif item_to_use.effect == "add_credits":
            self.update_credits(player, int(item_to_use.effect_value), "Used Credit Chip")
            effect_msg = f"Added {item_to_use.effect_value} credits."
        else:
            return False, f"Unknown effect: {item_to_use.effect}"

        # Consume
        player.remove_item(item_id)
        self.repository.save(player)
        self.logger.info(f"Player {player.name} used item {item_to_use.name}")

        return True, f"Used {item_to_use.name}. {effect_msg}"
