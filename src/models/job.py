"""
Job data model for offline jobs
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid

class JobType(Enum):
    """Job type enumeration"""
    IT_SUPPORT = "it_support"  # Multiple choice
    SCRIPTING = "scripting"    # Script submission

class JobDifficulty(Enum):
    """Job difficulty enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class JobOption:
    """Option for multiple choice jobs"""
    id: str
    text: str
    result_text: str
    credits_change: int = 0
    reputation_change: int = 0
    heat_change: int = 0
    required_item: Optional[str] = None

@dataclass
class Job:
    """Job class"""
    id: str
    title: str
    description: str
    employer: str
    job_type: JobType
    difficulty: JobDifficulty
    reward_credits: int
    reward_xp: int
    reward_items: Dict[str, int] = field(default_factory=dict)

    # For IT_SUPPORT jobs
    options: List[JobOption] = field(default_factory=list)

    # For SCRIPTING jobs
    script_validation_regex: Optional[str] = None
    script_expected_output: Optional[str] = None

    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "employer": self.employer,
            "job_type": self.job_type.value,
            "difficulty": self.difficulty.value,
            "reward_credits": self.reward_credits,
            "reward_xp": self.reward_xp,
            "reward_items": self.reward_items,
            "options": [
                {
                    "id": opt.id,
                    "text": opt.text,
                    "result_text": opt.result_text,
                    "credits_change": opt.credits_change,
                    "reputation_change": opt.reputation_change,
                    "heat_change": opt.heat_change,
                    "required_item": opt.required_item
                }
                for opt in self.options
            ],
            "script_validation_regex": self.script_validation_regex,
            "script_expected_output": self.script_expected_output,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        job = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            employer=data["employer"],
            job_type=JobType(data["job_type"]),
            difficulty=JobDifficulty(data["difficulty"]),
            reward_credits=data["reward_credits"],
            reward_xp=data["reward_xp"],
            reward_items=data.get("reward_items", {})
        )

        if "options" in data:
            for opt_data in data["options"]:
                job.options.append(JobOption(
                    id=opt_data["id"],
                    text=opt_data["text"],
                    result_text=opt_data["result_text"],
                    credits_change=opt_data.get("credits_change", 0),
                    reputation_change=opt_data.get("reputation_change", 0),
                    heat_change=opt_data.get("heat_change", 0),
                    required_item=opt_data.get("required_item")
                ))

        job.script_validation_regex = data.get("script_validation_regex")
        job.script_expected_output = data.get("script_expected_output")

        if data.get("expires_at"):
            job.expires_at = datetime.fromisoformat(data["expires_at"])
        if data.get("created_at"):
            job.created_at = datetime.fromisoformat(data["created_at"])

        return job
