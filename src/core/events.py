"""
Event system for Nexus Root MMORPG
"""

from typing import Dict, Any, Callable, List
from abc import ABC, abstractmethod
from datetime import datetime
from .logger import NexusLogger

class Event:
    """Base event class"""
    def __init__(self, event_type: str, data: Dict[str, Any] = None, source: str = None):
        self.event_type = event_type
        self.data = data or {}
        self.source = source
        self.timestamp = datetime.now()
        self.id = f"{event_type}_{self.timestamp.timestamp()}"

class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    @abstractmethod
    def handle(self, event: Event) -> bool:
        """Handle an event. Return True if event was handled successfully."""
        pass

class EventBus:
    """Central event bus for pub/sub messaging"""
    
    def __init__(self):
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.logger = NexusLogger.get_logger("events")
    
    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe an event handler to an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        self.logger.debug(f"Subscribed {handler.__class__.__name__} to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler):
        """Unsubscribe an event handler from an event type"""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                self.logger.debug(f"Unsubscribed {handler.__class__.__name__} from {event_type}")
            except ValueError:
                pass
    
    def publish(self, event: Event):
        """Publish an event to all registered handlers"""
        self.logger.debug(f"Publishing event: {event.event_type}")
        
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                try:
                    success = handler.handle(event)
                    if not success:
                        self.logger.warning(f"Handler {handler.__class__.__name__} failed to handle {event.event_type}")
                except Exception as e:
                    self.logger.error(f"Error in handler {handler.__class__.__name__} for {event.event_type}: {str(e)}")

# Predefined event types
class PlayerEvents:
    """Player-related event types"""
    PLAYER_CREATED = "player.created"
    PLAYER_LOGGED_IN = "player.logged_in"
    PLAYER_LOGGED_OUT = "player.logged_out"
    PLAYER_LEVEL_UP = "player.level_up"
    PLAYER_CREDITS_CHANGED = "player.credits_changed"
    PLAYER_UPGRADED_HARDWARE = "player.upgraded_hardware"

class GameEvents:
    """Game-related event types"""
    COMMAND_EXECUTED = "game.command_executed"
    MISSION_COMPLETED = "game.mission_completed"
    MISSION_FAILED = "game.mission_failed"
    SCRIPT_EXECUTED = "game.script_executed"
    PASSIVE_MINING_STARTED = "game.passive_mining_started"
    PASSIVE_MINING_COMPLETED = "game.passive_mining_completed"

class SystemEvents:
    """System-related event types"""
    SERVER_STARTED = "system.server_started"
    SERVER_STOPPED = "system.server_stopped"
    ERROR_OCCURRED = "system.error_occurred"
    MAINTENANCE_MODE = "system.maintenance_mode"