"""
SQLite implementation of player repository
"""

import sqlite3
import json
import uuid
from typing import List, Optional
from ..models.player import Player
from .base_repository import BaseRepository
from ..core.exceptions import DatabaseError
from ..core.logger import NexusLogger

class SQLitePlayerRepository(BaseRepository):
    """SQLite implementation of player repository"""
    
    def __init__(self, db_path: str = "nexus_root.db"):
        self.db_path = db_path
        self.logger = NexusLogger.get_logger("player_repository")
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id TEXT PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        is_vip BOOLEAN DEFAULT FALSE,
                        session_id TEXT,
                        created_at TEXT NOT NULL,
                        last_login TEXT NOT NULL,
                        is_online BOOLEAN DEFAULT FALSE,
                        password_hash TEXT,
                        data TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS admin_users (
                        id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS banned_ips (
                        id TEXT PRIMARY KEY,
                        ip_address TEXT UNIQUE NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        admin_id TEXT,
                        player_id TEXT,
                        token TEXT UNIQUE NOT NULL,
                        FOREIGN KEY (admin_id) REFERENCES admin_users (id),
                        FOREIGN KEY (player_id) REFERENCES players (id)
                    )
                """)

                # Create indices
                conn.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_players_session ON players(session_id)")
                
                conn.commit()
                self.logger.debug("Initialized player and admin tables")
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize tables: {str(e)}")
    
    def save(self, player: Player) -> Player:
        """Save a player"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Generate ID if new player
                if not player.id:
                    player.id = str(uuid.uuid4())
                
                # Serialize player data
                player_data = player.to_dict()
                data_json = json.dumps(player_data)
                
                # Insert or update
                conn.execute("""
                    INSERT OR REPLACE INTO players 
                    (id, name, is_vip, session_id, created_at, last_login, is_online, password_hash, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player.id,
                    player.name,
                    player.is_vip,
                    player.session_id,
                    player.created_at.isoformat(),
                    player.last_login.isoformat(),
                    player.is_online,
                    getattr(player, 'password_hash', None),
                    data_json
                ))
                
                conn.commit()
                self.logger.debug(f"Saved player: {player.name}")
                
            return player
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save player {player.name}: {str(e)}")
    
    def find_by_id(self, player_id: str) -> Optional[Player]:
        """Find player by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM players WHERE id = ?",
                    (player_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    player_data = json.loads(row[0])
                    return Player.from_dict(player_data)
                
                return None
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find player by ID {player_id}: {str(e)}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Failed to deserialize player data: {str(e)}")
    
    def find_by_name(self, name: str) -> Optional[Player]:
        """Find player by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM players WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                
                if row:
                    player_data = json.loads(row[0])
                    return Player.from_dict(player_data)
                
                return None
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find player by name {name}: {str(e)}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Failed to deserialize player data: {str(e)}")
    
    def find_by_session_id(self, session_id: str) -> Optional[Player]:
        """Find player by session ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM players WHERE session_id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    player_data = json.loads(row[0])
                    return Player.from_dict(player_data)
                
                return None
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find player by session ID {session_id}: {str(e)}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Failed to deserialize player data: {str(e)}")
    
    def find_all(self) -> List[Player]:
        """Find all players"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM players ORDER BY created_at")
                rows = cursor.fetchall()
                
                players = []
                for row in rows:
                    try:
                        player_data = json.loads(row[0])
                        players.append(Player.from_dict(player_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted player data")
                
                return players
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find all players: {str(e)}")
    
    def get_online_players(self) -> List[Player]:
        """Find all online players"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM players WHERE is_online = TRUE ORDER BY last_login DESC"
                )
                rows = cursor.fetchall()
                
                players = []
                for row in rows:
                    try:
                        player_data = json.loads(row[0])
                        players.append(Player.from_dict(player_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted player data")
                
                return players
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find online players: {str(e)}")
    
    def get_leaderboard(self, category: str = "level", limit: int = 10) -> List[Player]:
        """Get player leaderboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Use JSON extraction for sorting
                if category == "level":
                    order_clause = "json_extract(data, '$.stats.level') DESC"
                elif category == "credits":
                    order_clause = "json_extract(data, '$.stats.credits') DESC"
                elif category == "missions":
                    order_clause = "json_extract(data, '$.stats.total_missions_completed') DESC"
                else:
                    order_clause = "json_extract(data, '$.stats.level') DESC"
                
                cursor = conn.execute(f"""
                    SELECT data FROM players 
                    ORDER BY {order_clause}
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                
                players = []
                for row in rows:
                    try:
                        player_data = json.loads(row[0])
                        players.append(Player.from_dict(player_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted player data")
                
                return players
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get leaderboard: {str(e)}")
    
    def delete(self, player_id: str) -> bool:
        """Delete a player"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM players WHERE id = ?",
                    (player_id,)
                )
                
                conn.commit()
                deleted = cursor.rowcount > 0
                
                if deleted:
                    self.logger.info(f"Deleted player: {player_id}")
                
                return deleted
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete player {player_id}: {str(e)}")
    
    def count(self) -> int:
        """Count total players"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM players")
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to count players: {str(e)}")
    
    def count_online(self) -> int:
        """Count online players"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM players WHERE is_online = TRUE")
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to count online players: {str(e)}")
    
    def cleanup_old_sessions(self, hours_ago: int = 24):
        """Clean up old sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE players 
                    SET is_online = FALSE, session_id = NULL 
                    WHERE is_online = TRUE 
                    AND datetime(last_login) < datetime('now', '-{} hours')
                """.format(hours_ago))
                
                conn.commit()
                self.logger.info(f"Cleaned up sessions older than {hours_ago} hours")
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to cleanup old sessions: {str(e)}")