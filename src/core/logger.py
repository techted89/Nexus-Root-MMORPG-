"""
Centralized logging system for Nexus Root MMORPG
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class NexusLogger:
    """Centralized logging system with structured logging support"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """Initialize the logging system"""
        if cls._initialized:
            return
            
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger("nexus")
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s.%(levelname)s: %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_dir / log_file)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger for the given name"""
        if not cls._initialized:
            cls.initialize()
            
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(f"nexus.{name}")
            
        return cls._loggers[name]
    
    @classmethod
    def log_event(cls, event_type: str, data: Dict[str, Any], level: str = "INFO"):
        """Log a structured event"""
        logger = cls.get_logger("events")
        message = f"{event_type}: {data}"
        getattr(logger, level.lower())(message)
    
    @classmethod
    def log_command(cls, player_name: str, command: str, success: bool, duration_ms: float):
        """Log command execution"""
        logger = cls.get_logger("commands")
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"COMMAND {status}: player={player_name} cmd='{command}' duration={duration_ms:.2f}ms")
    
    @classmethod
    def log_error(cls, error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        logger = cls.get_logger("errors")
        context_str = f" context={context}" if context else ""
        logger.error(f"ERROR: {type(error).__name__}: {str(error)}{context_str}", exc_info=True)