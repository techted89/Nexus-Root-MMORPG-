"""
Base repository interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseRepository(ABC):
    """Abstract base repository interface"""
    
    @abstractmethod
    def save(self, entity) -> Any:
        """Save an entity"""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[Any]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Any]:
        """Find all entities"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Count total entities"""
        pass