"""
Item and Equipment data models
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class ItemType(Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    CONSUMABLE = "consumable"
    MATERIAL = "material"

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Item:
    id: str
    name: str
    type: ItemType
    rarity: ItemRarity
    description: str
    value: int
    stackable: bool = False
    quantity: int = 1

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "rarity": self.rarity.value,
            "description": self.description,
            "value": self.value,
            "stackable": self.stackable,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            name=data["name"],
            type=ItemType(data["type"]),
            rarity=ItemRarity(data["rarity"]),
            description=data["description"],
            value=data["value"],
            stackable=data.get("stackable", False),
            quantity=data.get("quantity", 1)
        )

@dataclass
class Equipment(Item):
    slot: str = "none" # cpu, ram, network, storage, expansion
    stats: Dict[str, float] = field(default_factory=dict)
    level_requirement: int = 1

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "slot": self.slot,
            "stats": self.stats,
            "level_requirement": self.level_requirement
        })
        return data

    @classmethod
    def from_dict(cls, data):
        item = super().from_dict(data)
        return cls(
            id=item.id,
            name=item.name,
            type=item.type,
            rarity=item.rarity,
            description=item.description,
            value=item.value,
            stackable=item.stackable,
            quantity=item.quantity,
            slot=data.get("slot", "none"),
            stats=data.get("stats", {}),
            level_requirement=data.get("level_requirement", 1)
        )

@dataclass
class Consumable(Item):
    effect: str = "none" # restore_heat, boost_speed, etc.
    effect_value: float = 0.0
    duration_seconds: int = 0

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "effect": self.effect,
            "effect_value": self.effect_value,
            "duration_seconds": self.duration_seconds
        })
        return data

    @classmethod
    def from_dict(cls, data):
        item = super().from_dict(data)
        return cls(
            id=item.id,
            name=item.name,
            type=item.type,
            rarity=item.rarity,
            description=item.description,
            value=item.value,
            stackable=item.stackable,
            quantity=item.quantity,
            effect=data.get("effect", "none"),
            effect_value=data.get("effect_value", 0.0),
            duration_seconds=data.get("duration_seconds", 0)
        )
