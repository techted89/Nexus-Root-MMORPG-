"""
Configuration management for Nexus Root MMORPG
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from .exceptions import ConfigurationError
from .logger import NexusLogger

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "nexus_root.db"
    username: str = ""
    password: str = ""
    pool_size: int = 5

@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    workers: int = 1

@dataclass
class GameConfig:
    """Game configuration"""
    max_players: int = 1000
    max_threads_per_player: int = 10
    credit_multiplier: float = 1.0
    xp_multiplier: float = 1.0
    passive_mining_enabled: bool = True

@dataclass
class NexusConfig:
    """Main configuration class"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    game: GameConfig = field(default_factory=GameConfig)
    log_level: str = "INFO"
    log_file: str = "nexus.log"
    
    @classmethod
    def load_from_file(cls, config_path: str = "config.json") -> "NexusConfig":
        """Load configuration from file"""
        logger = NexusLogger.get_logger("config")
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
            else:
                config_data = {}
                logger.info(f"No config file found at {config_path}, using defaults")
            
            # Parse nested configs
            database_config = DatabaseConfig(**config_data.get("database", {}))
            server_config = ServerConfig(**config_data.get("server", {}))
            game_config = GameConfig(**config_data.get("game", {}))
            
            return cls(
                database=database_config,
                server=server_config,
                game=game_config,
                log_level=config_data.get("log_level", "INFO"),
                log_file=config_data.get("log_file", "nexus.log")
            )
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    @classmethod
    def load_from_env(cls) -> "NexusConfig":
        """Load configuration from environment variables"""
        return cls(
            database=DatabaseConfig(
                type=os.getenv("NEXUS_DB_TYPE", "sqlite"),
                host=os.getenv("NEXUS_DB_HOST", "localhost"),
                port=int(os.getenv("NEXUS_DB_PORT", "5432")),
                database=os.getenv("NEXUS_DB_NAME", "nexus_root.db"),
                username=os.getenv("NEXUS_DB_USER", ""),
                password=os.getenv("NEXUS_DB_PASS", ""),
            ),
            server=ServerConfig(
                host=os.getenv("NEXUS_SERVER_HOST", "0.0.0.0"),
                port=int(os.getenv("NEXUS_SERVER_PORT", "8080")),
                debug=os.getenv("NEXUS_DEBUG", "false").lower() == "true",
                workers=int(os.getenv("NEXUS_WORKERS", "1")),
            ),
            game=GameConfig(
                max_players=int(os.getenv("NEXUS_MAX_PLAYERS", "1000")),
                max_threads_per_player=int(os.getenv("NEXUS_MAX_THREADS", "10")),
                credit_multiplier=float(os.getenv("NEXUS_CREDIT_MULT", "1.0")),
                xp_multiplier=float(os.getenv("NEXUS_XP_MULT", "1.0")),
            ),
            log_level=os.getenv("NEXUS_LOG_LEVEL", "INFO"),
            log_file=os.getenv("NEXUS_LOG_FILE", "nexus.log"),
        )
    
    def save_to_file(self, config_path: str = "config.json"):
        """Save configuration to file"""
        config_data = {
            "database": {
                "type": self.database.type,
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "password": self.database.password,
                "pool_size": self.database.pool_size,
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "debug": self.server.debug,
                "workers": self.server.workers,
            },
            "game": {
                "max_players": self.game.max_players,
                "max_threads_per_player": self.game.max_threads_per_player,
                "credit_multiplier": self.game.credit_multiplier,
                "xp_multiplier": self.game.xp_multiplier,
                "passive_mining_enabled": self.game.passive_mining_enabled,
            },
            "log_level": self.log_level,
            "log_file": self.log_file,
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger = NexusLogger.get_logger("config")
        logger.info(f"Configuration saved to {config_path}")