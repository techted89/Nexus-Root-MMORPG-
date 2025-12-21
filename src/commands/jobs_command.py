"""
Jobs command implementation
"""

from typing import List, Dict, Any
from ..services.command_service import Command, CommandResult
from ..models.player import Player
from ..services.job_service import JobService
from ..models.job import JobType

class JobsCommand(Command):
    """Command to manage offline jobs"""

    def __init__(self, job_service: JobService):
        super().__init__("jobs", "Manage freelance jobs", "jobs [list|accept|complete|info] [args]")
        self.job_service = job_service

    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: jobs [list|info|complete]")

        subcommand = args[0]

        if subcommand == "list":
            jobs = self.job_service.get_player_jobs(player)
            if not jobs:
                return CommandResult(True, "No jobs available right now.")

            output = "Available Jobs:\n"
            output += f"{'ID':<4} {'Title':<20} {'Type':<12} {'Difficulty':<10} {'Employer'}\n"
            output += "-" * 60 + "\n"

            for i, job in enumerate(jobs):
                # We use the index as a temporary ID for the user to interact with
                # In a real persistence layer, we'd use the UUID, but typing UUIDs is hard
                output += f"{i+1:<4} {job.title:<20} {job.job_type.value:<12} {job.difficulty.value:<10} {job.employer}\n"

            return CommandResult(True, output, data={"jobs": [j.to_dict() for j in jobs]})

        elif subcommand == "info":
            if len(args) < 2:
                return CommandResult(False, error="Usage: jobs info <job_number>")

            try:
                index = int(args[1]) - 1
                jobs = self.job_service.get_player_jobs(player)
                if index < 0 or index >= len(jobs):
                    return CommandResult(False, error="Invalid job number")

                job = jobs[index]

                output = f"Job: {job.title}\n"
                output += f"Employer: {job.employer}\n"
                output += f"Type: {job.job_type.value}\n"
                output += f"Difficulty: {job.difficulty.value}\n"
                output += f"Description: {job.description}\n\n"

                if job.job_type == JobType.IT_SUPPORT:
                    output += "Options:\n"
                    for i, option in enumerate(job.options):
                        output += f"{i+1}. {option.text}\n"
                    output += "\nUse 'jobs complete <job_number> <option_number>' to choose."

                elif job.job_type == JobType.SCRIPTING:
                    output += f"Objective: {job.script_expected_output}\n" # Simplified for now
                    output += "\nUse 'jobs complete <job_number> <script_output>' to verify."
                    # Note: In a real scenario, this would take a script filename, execute it, and check output.
                    # For this simulation, we might ask them to pass the output string or a filename if we can cat it.

                return CommandResult(True, output, data={"job": job.to_dict()})

            except ValueError:
                return CommandResult(False, error="Job number must be an integer")

        elif subcommand == "complete":
            if len(args) < 3:
                return CommandResult(False, error="Usage: jobs complete <job_number> <choice/script_output>")

            try:
                index = int(args[1]) - 1
                jobs = self.job_service.get_player_jobs(player)
                if index < 0 or index >= len(jobs):
                    return CommandResult(False, error="Invalid job number")

                job = jobs[index]

                result = None

                if job.job_type == JobType.IT_SUPPORT:
                    try:
                        choice_index = int(args[2]) - 1
                        result = self.job_service.complete_job(player, job.id, choice_index=choice_index)
                    except ValueError:
                        return CommandResult(False, error="Choice must be a number")

                elif job.job_type == JobType.SCRIPTING:
                    # For scripting, if the 3rd arg is a filename, we should read it?
                    # Or execute it?
                    # As per instruction "some jobs will require script request to complete a task"
                    # We can assume the user runs the script and pipes output? Or we run it.
                    # Let's assume the user passes the output string for now as a simple verification,
                    # OR if the user passes a filename, we check if it exists (but we can't run it here easily without execution context).
                    # Actually, better integration: "jobs verify <job_id> <script_file>"

                    # For this implementation, let's treat the rest of args as the "output" string they manually type (or copy paste)
                    # Or better: "jobs complete <id> $(run myscript.ns)" if the shell supported subshells.

                    # Let's interpret the 3rd arg as a literal string for now to match against expected output.
                    script_output = " ".join(args[2:])
                    result = self.job_service.complete_job(player, job.id, script_output=script_output)

                if result:
                    if result["success"]:
                        return CommandResult(True, f"Job Completed!\n{result['message']}\nReceived: {result.get('credits',0)} credits, {result.get('xp',0)} XP.")
                    else:
                        return CommandResult(False, error=f"Job Failed: {result['message']}")

                return CommandResult(False, error="Unknown error processing job")

            except ValueError:
                return CommandResult(False, error="Job number must be an integer")

        else:
            return CommandResult(False, error="Unknown subcommand. Usage: jobs [list|info|complete]")
