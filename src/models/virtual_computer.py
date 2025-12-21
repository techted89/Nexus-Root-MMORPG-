"""
Virtual Computer data model
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from .item import Equipment, ItemType, ItemRarity

@dataclass
class VirtualComputer:
    """Virtual Computer representing player's system"""
    
    def __init__(self):
        # Slots for Equipment
        self.cpu_slot: Optional[Equipment] = None
        self.ram_slot: Optional[Equipment] = None
        self.network_slot: Optional[Equipment] = None
        self.storage_slot: Optional[Equipment] = None

        # Legacy Tiers (Fallback / Base stats if no item equipped)
        self.cpu_tier: int = 1
        self.ram_tier: int = 1
        self.nic_tier: int = 1
        self.ssd_tier: int = 1
        
        # System state
        self.active_threads: int = 0
        self.passive_mining_end_time: Optional[datetime] = None
        self.last_maintenance: datetime = datetime.now()
        
        # Heat Mechanic
        self.current_heat: float = 0.0
        self.max_heat: float = 100.0
        self.cooling_rate: float = 2.0
        self.last_heat_update: datetime = datetime.now()

        # Performance metrics
        self.total_uptime_minutes: int = 0
        self.total_commands_processed: int = 0
        
    def get_cpu_speed(self) -> float:
        """Calculate total CPU speed multiplier"""
        base = max(0.1, 1.0 - (self.cpu_tier - 1) * 0.1)
        if self.cpu_slot:
            # Equipment modifiers (lower is faster for speed_multiplier logic usually, or higher is better?)
            # Existing logic: lower multiplier = faster execution.
            # Let's assume stats add bonus speed.
            # speed_multiplier = base - item_bonus
            bonus = self.cpu_slot.stats.get("speed_bonus", 0.0)
            return max(0.1, base - bonus)
        return base

    def get_max_threads(self) -> int:
        """Calculate max threads"""
        base = min(5, (self.ram_tier + 1) // 2)
        if self.ram_slot:
            base += int(self.ram_slot.stats.get("threads_bonus", 0))
        return base

    def get_network_bandwidth(self) -> int:
        base = 10 * self.nic_tier
        if self.network_slot:
            base += int(self.network_slot.stats.get("bandwidth_bonus", 0))
        return base

    def get_storage_capacity(self) -> int:
        base = 100 * self.ssd_tier
        if self.storage_slot:
            base += int(self.storage_slot.stats.get("capacity_bonus", 0))
        return base

    def can_run_threads(self, thread_count: int) -> bool:
        return (self.active_threads + thread_count) <= self.get_max_threads()

    def update_heat(self):
        now = datetime.now()
        elapsed_seconds = (now - self.last_heat_update).total_seconds()

        if elapsed_seconds > 0:
            # Cooling rate bonus from equipment?
            effective_cooling = self.cooling_rate
            # Check fan/cooling items if we had a slot, or maybe CPU slot has cooling stat
            if self.cpu_slot:
                effective_cooling += self.cpu_slot.stats.get("cooling_bonus", 0.0)

            cooling_amount = elapsed_seconds * effective_cooling
            self.current_heat = max(0.0, self.current_heat - cooling_amount)
            self.last_heat_update = now

    def add_heat(self, amount: float):
        self.update_heat()
        # Resistance?
        resistance = 0.0
        if self.cpu_slot:
            resistance = self.cpu_slot.stats.get("heat_resistance", 0.0)

        actual_amount = max(0, amount * (1.0 - resistance))
        self.current_heat = min(self.max_heat, self.current_heat + actual_amount)

    def is_overheated(self) -> bool:
        self.update_heat()
        return self.current_heat >= (self.max_heat * 0.95)
    
    def start_passive_mining(self, duration_hours: int) -> bool:
        if self.passive_mining_end_time and datetime.now() < self.passive_mining_end_time:
            return False
        self.passive_mining_end_time = datetime.now() + timedelta(hours=duration_hours)
        return True
    
    def check_passive_mining(self) -> Optional[int]:
        if not self.passive_mining_end_time:
            return None
        if datetime.now() >= self.passive_mining_end_time:
            self.passive_mining_end_time = None
            return 100
        return None
    
    def get_passive_mining_time_remaining(self) -> Optional[timedelta]:
        if not self.passive_mining_end_time:
            return None
        remaining = self.passive_mining_end_time - datetime.now()
        return remaining if remaining.total_seconds() > 0 else None
    
    # Legacy upgrade method support (upgrades base tier)
    def upgrade_component(self, component_name: str) -> tuple[bool, int]:
        # Simple cost logic for tiers
        tier = 0
        if component_name == "cpu": tier = self.cpu_tier
        elif component_name == "ram": tier = self.ram_tier
        elif component_name == "nic": tier = self.nic_tier
        elif component_name == "ssd": tier = self.ssd_tier
        else: return False, 0
        
        if tier >= 10: return False, 0
        
        cost = 50 * (2 ** (tier - 1))
        
        if component_name == "cpu": self.cpu_tier += 1
        elif component_name == "ram": self.ram_tier += 1
        elif component_name == "nic": self.nic_tier += 1
        elif component_name == "ssd": self.ssd_tier += 1
        
        return True, cost
    
    def get_all_components_info(self) -> Dict[str, any]:
        # Combined legacy + equipment info
        return {
            "cpu": {"tier": self.cpu_tier, "item": self.cpu_slot.to_dict() if self.cpu_slot else None},
            "ram": {"tier": self.ram_tier, "item": self.ram_slot.to_dict() if self.ram_slot else None},
            "nic": {"tier": self.nic_tier, "item": self.network_slot.to_dict() if self.network_slot else None},
            "ssd": {"tier": self.ssd_tier, "item": self.storage_slot.to_dict() if self.storage_slot else None}
        }
    
    def get_system_stats(self) -> Dict[str, any]:
        self.update_heat()
        return {
            "cpu_tier": self.cpu_tier,
            "ram_tier": self.ram_tier,
            "nic_tier": self.nic_tier,
            "ssd_tier": self.ssd_tier,
            "active_threads": self.active_threads,
            "max_threads": self.get_max_threads(),
            "cpu_speed_multiplier": self.get_cpu_speed(),
            "network_bandwidth": self.get_network_bandwidth(),
            "storage_capacity": self.get_storage_capacity(),
            "passive_mining_active": self.passive_mining_end_time is not None,
            "mining_time_remaining": self.get_passive_mining_time_remaining(),
            "total_uptime_minutes": self.total_uptime_minutes,
            "total_commands_processed": self.total_commands_processed,
            "heat": self.current_heat,
            "max_heat": self.max_heat
        }
    
    def get_summary(self) -> Dict[str, any]:
        self.update_heat()
        return {
            "cpu_tier": self.cpu_tier,
            "ram_tier": self.ram_tier,
            "active_threads": self.active_threads,
            "max_threads": self.get_max_threads(),
            "heat": self.current_heat,
            "max_heat": self.max_heat
        }
    
    def to_dict(self) -> Dict[str, any]:
        return {
            "cpu_tier": self.cpu_tier,
            "ram_tier": self.ram_tier,
            "nic_tier": self.nic_tier,
            "ssd_tier": self.ssd_tier,
            "cpu_slot": self.cpu_slot.to_dict() if self.cpu_slot else None,
            "ram_slot": self.ram_slot.to_dict() if self.ram_slot else None,
            "network_slot": self.network_slot.to_dict() if self.network_slot else None,
            "storage_slot": self.storage_slot.to_dict() if self.storage_slot else None,
            "active_threads": self.active_threads,
            "passive_mining_end_time": self.passive_mining_end_time.isoformat() if self.passive_mining_end_time else None,
            "last_maintenance": self.last_maintenance.isoformat(),
            "total_uptime_minutes": self.total_uptime_minutes,
            "total_commands_processed": self.total_commands_processed,
            "heat": self.current_heat,
            "last_heat_update": self.last_heat_update.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "VirtualComputer":
        vc = cls()
        vc.cpu_tier = data.get("cpu_tier", 1)
        vc.ram_tier = data.get("ram_tier", 1)
        vc.nic_tier = data.get("nic_tier", 1)
        vc.ssd_tier = data.get("ssd_tier", 1)
        
        if data.get("cpu_slot"): vc.cpu_slot = Equipment.from_dict(data["cpu_slot"])
        if data.get("ram_slot"): vc.ram_slot = Equipment.from_dict(data["ram_slot"])
        if data.get("network_slot"): vc.network_slot = Equipment.from_dict(data["network_slot"])
        if data.get("storage_slot"): vc.storage_slot = Equipment.from_dict(data["storage_slot"])
        
        vc.active_threads = data.get("active_threads", 0)
        
        if data.get("passive_mining_end_time"):
            vc.passive_mining_end_time = datetime.fromisoformat(data["passive_mining_end_time"])
        
        if data.get("last_maintenance"):
            vc.last_maintenance = datetime.fromisoformat(data["last_maintenance"])
        
        vc.total_uptime_minutes = data.get("total_uptime_minutes", 0)
        vc.total_commands_processed = data.get("total_commands_processed", 0)
        
        vc.current_heat = float(data.get("heat", 0.0))
        if data.get("last_heat_update"):
            vc.last_heat_update = datetime.fromisoformat(data["last_heat_update"])

        return vc
