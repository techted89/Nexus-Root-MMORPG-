"""
Virtual Computer data model
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime, timedelta

@dataclass
class Hardware:
    """Hardware component base class"""
    tier: int = 1
    max_tier: int = 10
    
    def can_upgrade(self) -> bool:
        """Check if hardware can be upgraded"""
        return self.tier < self.max_tier
    
    def upgrade(self) -> bool:
        """Upgrade hardware tier"""
        if self.can_upgrade():
            self.tier += 1
            return True
        return False

@dataclass
class CPU(Hardware):
    """CPU component"""
    
    def get_speed_multiplier(self) -> float:
        """Get speed multiplier based on tier"""
        # Higher tier = faster execution (lower multiplier)
        return max(0.1, 1.0 - (self.tier - 1) * 0.1)
    
    def get_cost_for_next_tier(self) -> int:
        """Get cost for upgrading to next tier"""
        if not self.can_upgrade():
            return 0
        return 50 * (2 ** (self.tier - 1))

@dataclass
class RAM(Hardware):
    """RAM component"""
    
    def get_max_threads(self) -> int:
        """Get maximum threads based on tier"""
        return min(5, (self.tier + 1) // 2)
    
    def get_cost_for_next_tier(self) -> int:
        """Get cost for upgrading to next tier"""
        if not self.can_upgrade():
            return 0
        return 50 * (2 ** (self.tier - 1))

@dataclass
class NetworkCard(Hardware):
    """Network Interface Card component"""
    
    def get_bandwidth(self) -> int:
        """Get network bandwidth in Mbps"""
        return 10 * self.tier
    
    def get_cost_for_next_tier(self) -> int:
        """Get cost for upgrading to next tier"""
        if not self.can_upgrade():
            return 0
        return 75 * (2 ** (self.tier - 1))

@dataclass
class Storage(Hardware):
    """Storage component"""
    
    def get_capacity(self) -> int:
        """Get storage capacity in GB"""
        return 100 * self.tier
    
    def get_cost_for_next_tier(self) -> int:
        """Get cost for upgrading to next tier"""
        if not self.can_upgrade():
            return 0
        return 25 * (2 ** (self.tier - 1))

class VirtualComputer:
    """Virtual Computer representing player's system"""
    
    def __init__(self):
        self.cpu = CPU()
        self.ram = RAM()
        self.network_card = NetworkCard()
        self.storage = Storage()
        
        # System state
        self.active_threads: int = 0
        self.passive_mining_end_time: Optional[datetime] = None
        self.last_maintenance: datetime = datetime.now()
        
        # Performance metrics
        self.total_uptime_minutes: int = 0
        self.total_commands_processed: int = 0
        
    def can_run_threads(self, thread_count: int) -> bool:
        """Check if system can run specified number of threads"""
        return (self.active_threads + thread_count) <= self.ram.get_max_threads()
    
    def start_passive_mining(self, duration_hours: int) -> bool:
        """Start passive hash mining"""
        if self.passive_mining_end_time and datetime.now() < self.passive_mining_end_time:
            return False  # Already mining
        
        self.passive_mining_end_time = datetime.now() + timedelta(hours=duration_hours)
        return True
    
    def check_passive_mining(self) -> Optional[int]:
        """Check passive mining status and return credits if completed"""
        if not self.passive_mining_end_time:
            return None
        
        if datetime.now() >= self.passive_mining_end_time:
            self.passive_mining_end_time = None
            return 100  # Base mining reward
        
        return None
    
    def get_passive_mining_time_remaining(self) -> Optional[timedelta]:
        """Get remaining time for passive mining"""
        if not self.passive_mining_end_time:
            return None
        
        remaining = self.passive_mining_end_time - datetime.now()
        return remaining if remaining.total_seconds() > 0 else None
    
    def upgrade_component(self, component_name: str) -> tuple[bool, int]:
        """Upgrade a component, returns (success, cost)"""
        component_map = {
            "cpu": self.cpu,
            "ram": self.ram,
            "nic": self.network_card,
            "ssd": self.storage
        }
        
        if component_name not in component_map:
            return False, 0
        
        component = component_map[component_name]
        cost = component.get_cost_for_next_tier()
        
        if cost == 0:  # Max tier reached
            return False, 0
        
        success = component.upgrade()
        return success, cost
    
    def get_component_info(self, component_name: str) -> Dict[str, any]:
        """Get information about a specific component"""
        component_map = {
            "cpu": self.cpu,
            "ram": self.ram,
            "nic": self.network_card,
            "ssd": self.storage
        }
        
        if component_name not in component_map:
            return {}
        
        component = component_map[component_name]
        
        info = {
            "name": component_name,
            "tier": component.tier,
            "max_tier": component.max_tier,
            "can_upgrade": component.can_upgrade(),
            "upgrade_cost": component.get_cost_for_next_tier()
        }
        
        # Add component-specific info
        if component_name == "cpu":
            info["speed_multiplier"] = component.get_speed_multiplier()
        elif component_name == "ram":
            info["max_threads"] = component.get_max_threads()
        elif component_name == "nic":
            info["bandwidth_mbps"] = component.get_bandwidth()
        elif component_name == "ssd":
            info["capacity_gb"] = component.get_capacity()
        
        return info
    
    def get_all_components_info(self) -> Dict[str, Dict[str, any]]:
        """Get information about all components"""
        return {
            "cpu": self.get_component_info("cpu"),
            "ram": self.get_component_info("ram"),
            "nic": self.get_component_info("nic"),
            "ssd": self.get_component_info("ssd")
        }
    
    def get_system_stats(self) -> Dict[str, any]:
        """Get system statistics"""
        return {
            "cpu_tier": self.cpu.tier,
            "ram_tier": self.ram.tier,
            "nic_tier": self.network_card.tier,
            "ssd_tier": self.storage.tier,
            "active_threads": self.active_threads,
            "max_threads": self.ram.get_max_threads(),
            "cpu_speed_multiplier": self.cpu.get_speed_multiplier(),
            "network_bandwidth": self.network_card.get_bandwidth(),
            "storage_capacity": self.storage.get_capacity(),
            "passive_mining_active": self.passive_mining_end_time is not None,
            "mining_time_remaining": self.get_passive_mining_time_remaining(),
            "total_uptime_minutes": self.total_uptime_minutes,
            "total_commands_processed": self.total_commands_processed
        }
    
    def get_summary(self) -> Dict[str, any]:
        """Get summary for API responses"""
        return {
            "cpu_tier": self.cpu.tier,
            "ram_tier": self.ram.tier,
            "nic_tier": self.network_card.tier,
            "ssd_tier": self.storage.tier,
            "active_threads": self.active_threads,
            "max_threads": self.ram.get_max_threads(),
            "passive_mining_active": self.passive_mining_end_time is not None
        }
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization"""
        return {
            "cpu_tier": self.cpu.tier,
            "ram_tier": self.ram.tier,
            "nic_tier": self.network_card.tier,
            "ssd_tier": self.storage.tier,
            "active_threads": self.active_threads,
            "passive_mining_end_time": self.passive_mining_end_time.isoformat() if self.passive_mining_end_time else None,
            "last_maintenance": self.last_maintenance.isoformat(),
            "total_uptime_minutes": self.total_uptime_minutes,
            "total_commands_processed": self.total_commands_processed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "VirtualComputer":
        """Create from dictionary"""
        vc = cls()
        
        vc.cpu.tier = data.get("cpu_tier", 1)
        vc.ram.tier = data.get("ram_tier", 1)
        vc.network_card.tier = data.get("nic_tier", 1)
        vc.storage.tier = data.get("ssd_tier", 1)
        
        vc.active_threads = data.get("active_threads", 0)
        
        if data.get("passive_mining_end_time"):
            vc.passive_mining_end_time = datetime.fromisoformat(data["passive_mining_end_time"])
        
        if data.get("last_maintenance"):
            vc.last_maintenance = datetime.fromisoformat(data["last_maintenance"])
        
        vc.total_uptime_minutes = data.get("total_uptime_minutes", 0)
        vc.total_commands_processed = data.get("total_commands_processed", 0)
        
        return vc