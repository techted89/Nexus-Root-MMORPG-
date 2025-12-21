"""
Job management service
"""

import random
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.job import Job, JobType, JobDifficulty, JobOption
from ..models.player import Player
from ..core.events import EventBus, Event
from ..core.logger import NexusLogger

class JobService:
    """Service for managing offline jobs"""

    def __init__(self, event_bus: EventBus = None):
        self.logger = NexusLogger.get_logger("job_service")
        self.event_bus = event_bus or EventBus()

        # Employers
        self.employers = [
            "TechCorp Inc.", "CyberDyne Systems", "Global Net", "Underground Collective",
            "SecureBank", "GovTech", "Shadow Brokers", "FreeNet"
        ]

        # Job templates for IT Support
        self.support_templates = [
            {
                "title": "Server Malfunction",
                "description": "One of our servers is acting up. The logs show high CPU usage.",
                "options": [
                    {
                        "text": "Reboot the server immediately.",
                        "result": "The server rebooted but data was corrupted. The client is unhappy.",
                        "credits": 50, "rep": -5, "heat": 0
                    },
                    {
                        "text": "Analyze logs and kill the rogue process.",
                        "result": "You found a crypto miner and removed it. The client is impressed.",
                        "credits": 150, "rep": 10, "heat": 0
                    },
                    {
                        "text": "Ignore it, it's probably fine.",
                        "result": "The server crashed an hour later.",
                        "credits": 0, "rep": -20, "heat": 0
                    }
                ]
            },
            {
                "title": "Suspicious Email",
                "description": "An employee received an email with a strange attachment.",
                "options": [
                    {
                        "text": "Delete the email without opening.",
                        "result": "Safe choice, but we never learned who sent it.",
                        "credits": 50, "rep": 0, "heat": 0
                    },
                    {
                        "text": "Open it in a sandbox environment.",
                        "result": "It was a zero-day exploit! You captured valuable data.",
                        "credits": 200, "rep": 20, "heat": 5
                    },
                    {
                        "text": "Forward it to everyone.",
                        "result": "The entire network is now infected. Good job.",
                        "credits": -100, "rep": -50, "heat": 20
                    }
                ]
            }
        ]

        # Job templates for Scripting
        self.script_templates = [
            {
                "title": "Automated Backup",
                "description": "Write a script that prints 'Backing up data...' to simulate a backup process.",
                "expected_output": "Backing up data...",
                "credits": 100, "xp": 50
            },
            {
                "title": "System Check",
                "description": "Write a script that outputs 'System OK'.",
                "expected_output": "System OK",
                "credits": 80, "xp": 40
            }
        ]

    def _get_difficulty_weights(self, level: int) -> List[float]:
        """Get weights for difficulty selection based on player level"""
        # Order: [EASY, MEDIUM, HARD]
        if level <= 3:
            return [0.7, 0.2, 0.1]
        elif level <= 7:
            return [0.3, 0.5, 0.2]
        else:
            return [0.1, 0.3, 0.6]

    def generate_jobs_for_player(self, player: Player, count: int = 3):
        """Generate new random jobs for a player"""
        new_jobs = []
        weights = self._get_difficulty_weights(player.stats.level)

        for _ in range(count):
            job_type = random.choice([JobType.IT_SUPPORT, JobType.SCRIPTING])
            difficulty = random.choices(list(JobDifficulty), weights=weights, k=1)[0]
            employer = random.choice(self.employers)

            if job_type == JobType.IT_SUPPORT:
                template = random.choice(self.support_templates)

                options = []
                for i, opt_data in enumerate(template["options"]):
                    options.append(JobOption(
                        id=str(i),
                        text=opt_data["text"],
                        result_text=opt_data["result"],
                        credits_change=opt_data.get("credits", 0),
                        reputation_change=opt_data.get("rep", 0),
                        heat_change=opt_data.get("heat", 0)
                    ))

                job = Job(
                    id=str(uuid.uuid4()),
                    title=template["title"],
                    description=template["description"],
                    employer=employer,
                    job_type=job_type,
                    difficulty=difficulty,
                    reward_credits=0, # Calculated based on choice
                    reward_xp=50, # Base XP
                    options=options,
                    expires_at=datetime.now() + timedelta(hours=24)
                )

            else: # SCRIPTING
                template = random.choice(self.script_templates)

                base_credits = template.get("credits", 100)
                base_xp = template.get("xp", 50)

                # Scale rewards by difficulty
                multiplier = 1.0
                if difficulty == JobDifficulty.MEDIUM: multiplier = 1.5
                elif difficulty == JobDifficulty.HARD: multiplier = 2.0

                job = Job(
                    id=str(uuid.uuid4()),
                    title=template["title"],
                    description=template["description"],
                    employer=employer,
                    job_type=job_type,
                    difficulty=difficulty,
                    reward_credits=int(base_credits * multiplier),
                    reward_xp=int(base_xp * multiplier),
                    script_expected_output=template.get("expected_output"),
                    expires_at=datetime.now() + timedelta(hours=24)
                )

            new_jobs.append(job)

        # Store jobs in player object as dicts
        player.active_jobs = [j.to_dict() for j in new_jobs]
        return new_jobs

    def get_player_jobs(self, player: Player) -> List[Job]:
        """Get available jobs for player"""
        # Load from player
        jobs_data = player.active_jobs
        jobs = [Job.from_dict(d) for d in jobs_data]

        # Filter expired
        current_time = datetime.now()
        active_jobs = [j for j in jobs if not j.expires_at or j.expires_at > current_time]

        # Save back if changed
        if len(active_jobs) != len(jobs):
             player.active_jobs = [j.to_dict() for j in active_jobs]

        # If empty, generate more
        if not active_jobs:
            return self.generate_jobs_for_player(player)

        return active_jobs

    def get_job(self, player: Player, job_id: str) -> Optional[Job]:
        """Get specific job"""
        jobs = self.get_player_jobs(player)
        for job in jobs:
            if job.id == job_id:
                return job
        return None

    def complete_job(self, player: Player, job_id: str, choice_index: int = None, script_output: str = None) -> Dict[str, Any]:
        """Complete a job"""
        job = self.get_job(player, job_id)
        if not job:
            return {"success": False, "message": "Job not found"}

        result = {}
        success = False

        if job.job_type == JobType.IT_SUPPORT:
            if choice_index is None or choice_index < 0 or choice_index >= len(job.options):
                return {"success": False, "message": "Invalid option selected"}

            option = job.options[choice_index]

            # Apply rewards/penalties
            credits_gain = option.credits_change
            if credits_gain != 0:
                player.update_credits(credits_gain)

            player.update_experience(job.reward_xp)

            # Apply heat (simulated for now, would need HeatService)
            if option.heat_change != 0:
                # TODO: Integrate with VirtualComputer heat
                pass

            result = {
                "success": True,
                "message": option.result_text,
                "credits": credits_gain,
                "xp": job.reward_xp
            }
            success = True

        elif job.job_type == JobType.SCRIPTING:
            if script_output is None:
                 return {"success": False, "message": "No script output provided"}

            # Simple check: Does output match expected?
            if job.script_expected_output and job.script_expected_output.strip() == script_output.strip():
                player.update_credits(job.reward_credits)
                player.update_experience(job.reward_xp)

                result = {
                    "success": True,
                    "message": "Script verification successful! Job completed.",
                    "credits": job.reward_credits,
                    "xp": job.reward_xp
                }
                success = True
            else:
                 return {
                    "success": False,
                    "message": f"Script output incorrect. Expected '{job.script_expected_output}', got '{script_output}'"
                }

        # Remove job from list
        if result.get("success"):
            # Update local list and player storage
            current_jobs = self.get_player_jobs(player)
            remaining_jobs = [j for j in current_jobs if j.id != job.id]
            player.active_jobs = [j.to_dict() for j in remaining_jobs]

            # Publish event
            self.event_bus.publish(Event(
                "job_completed",
                {
                    "player_id": player.id,
                    "player_data": player.to_dict(),  # Pass full player data to allow listeners to reconstruct player
                    "job_id": job.id,
                    "job_type": job.job_type.value,
                    "difficulty": job.difficulty.value
                },
                source="job_service"
            ))

        return result
