"""
SQLite implementation of mission repository
"""

import sqlite3
import json
from typing import List, Optional
from ..models.mission import Mission, MissionStatus
from .base_repository import BaseRepository
from ..core.exceptions import DatabaseError
from ..core.logger import NexusLogger

class SQLiteMissionRepository(BaseRepository):
    """SQLite implementation of mission repository"""
    
    def __init__(self, db_path: str = "nexus_root.db"):
        self.db_path = db_path
        self.logger = NexusLogger.get_logger("mission_repository")
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS missions (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        player_id TEXT,
                        created_at TEXT NOT NULL,
                        started_at TEXT,
                        completed_at TEXT,
                        data TEXT NOT NULL
                    )
                """)
                
                # Create indices
                conn.execute("CREATE INDEX IF NOT EXISTS idx_missions_player ON missions(player_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_missions_type ON missions(type)")
                
                conn.commit()
                self.logger.debug("Initialized mission tables")
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize mission tables: {str(e)}")
    
    def save(self, mission: Mission) -> Mission:
        """Save a mission"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Serialize mission data
                mission_data = mission.to_dict()
                data_json = json.dumps(mission_data)
                
                # Insert or update
                conn.execute("""
                    INSERT OR REPLACE INTO missions 
                    (id, name, type, status, player_id, created_at, started_at, completed_at, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mission.id,
                    mission.name,
                    mission.type.value,
                    mission.status.value,
                    mission.player_id,
                    mission.created_at.isoformat(),
                    mission.started_at.isoformat() if mission.started_at else None,
                    mission.completed_at.isoformat() if mission.completed_at else None,
                    data_json
                ))
                
                conn.commit()
                self.logger.debug(f"Saved mission: {mission.id}")
                
            return mission
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save mission {mission.id}: {str(e)}")
    
    def find_by_id(self, mission_id: str) -> Optional[Mission]:
        """Find mission by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM missions WHERE id = ?",
                    (mission_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    mission_data = json.loads(row[0])
                    return Mission.from_dict(mission_data)
                
                return None
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find mission by ID {mission_id}: {str(e)}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Failed to deserialize mission data: {str(e)}")
    
    def find_all(self) -> List[Mission]:
        """Find all missions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM missions ORDER BY created_at")
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    try:
                        mission_data = json.loads(row[0])
                        missions.append(Mission.from_dict(mission_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted mission data")
                
                return missions
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find all missions: {str(e)}")
    
    def find_by_player(self, player_id: str) -> List[Mission]:
        """Find missions by player ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM missions WHERE player_id = ? ORDER BY started_at DESC",
                    (player_id,)
                )
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    try:
                        mission_data = json.loads(row[0])
                        missions.append(Mission.from_dict(mission_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted mission data")
                
                return missions
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find missions for player {player_id}: {str(e)}")
    
    def find_by_status(self, status: MissionStatus) -> List[Mission]:
        """Find missions by status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM missions WHERE status = ? ORDER BY created_at",
                    (status.value,)
                )
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    try:
                        mission_data = json.loads(row[0])
                        missions.append(Mission.from_dict(mission_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted mission data")
                
                return missions
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find missions by status {status.value}: {str(e)}")
    
    def find_by_player_and_status(self, player_id: str, status: MissionStatus) -> List[Mission]:
        """Find missions by player and status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM missions WHERE player_id = ? AND status = ? ORDER BY started_at DESC",
                    (player_id, status.value)
                )
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    try:
                        mission_data = json.loads(row[0])
                        missions.append(Mission.from_dict(mission_data))
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted mission data")
                
                return missions
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find missions for player {player_id} with status {status.value}: {str(e)}")
    
    def find_available_for_player(self, player_level: int, completed_missions: List[str]) -> List[Mission]:
        """Find available missions for a player"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get missions that are available and meet level requirements
                cursor = conn.execute(
                    "SELECT data FROM missions WHERE status = 'available' ORDER BY created_at",
                )
                rows = cursor.fetchall()
                
                missions = []
                for row in rows:
                    try:
                        mission_data = json.loads(row[0])
                        mission = Mission.from_dict(mission_data)
                        
                        # Check level requirement
                        if mission.level_requirement > player_level:
                            continue
                        
                        # Check prerequisites
                        prereqs_met = all(prereq in completed_missions for prereq in mission.prerequisites)
                        if not prereqs_met:
                            continue
                        
                        missions.append(mission)
                        
                    except json.JSONDecodeError:
                        self.logger.warning("Skipped corrupted mission data")
                
                return missions
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to find available missions: {str(e)}")
    
    def count(self) -> int:
        """Count total missions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM missions")
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to count missions: {str(e)}")
    
    def count_by_status(self, status: MissionStatus) -> int:
        """Count missions by status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM missions WHERE status = ?",
                    (status.value,)
                )
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to count missions by status {status.value}: {str(e)}")
    
    def count_by_player(self, player_id: str) -> int:
        """Count missions for a player"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM missions WHERE player_id = ?",
                    (player_id,)
                )
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to count missions for player {player_id}: {str(e)}")
    
    def delete(self, mission_id: str) -> bool:
        """Delete a mission"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM missions WHERE id = ?",
                    (mission_id,)
                )
                
                conn.commit()
                deleted = cursor.rowcount > 0
                
                if deleted:
                    self.logger.info(f"Deleted mission: {mission_id}")
                
                return deleted
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete mission {mission_id}: {str(e)}")
    
    def cleanup_old_missions(self, days_ago: int = 30):
        """Clean up old completed missions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM missions 
                    WHERE status = 'completed' 
                    AND datetime(completed_at) < datetime('now', '-{} days')
                """.format(days_ago))
                
                conn.commit()
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} old missions")
                
                return deleted_count
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to cleanup old missions: {str(e)}")
    
    def get_mission_statistics(self) -> dict:
        """Get mission statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Total missions
                cursor = conn.execute("SELECT COUNT(*) FROM missions")
                stats['total'] = cursor.fetchone()[0]
                
                # By status
                cursor = conn.execute("""
                    SELECT status, COUNT(*) 
                    FROM missions 
                    GROUP BY status
                """)
                stats['by_status'] = dict(cursor.fetchall())
                
                # By type
                cursor = conn.execute("""
                    SELECT type, COUNT(*) 
                    FROM missions 
                    GROUP BY type
                """)
                stats['by_type'] = dict(cursor.fetchall())
                
                # Completion rate
                completed = stats['by_status'].get('completed', 0)
                total_started = completed + stats['by_status'].get('in_progress', 0) + stats['by_status'].get('failed', 0)
                stats['completion_rate'] = (completed / total_started * 100) if total_started > 0 else 0
                
                return stats
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get mission statistics: {str(e)}")