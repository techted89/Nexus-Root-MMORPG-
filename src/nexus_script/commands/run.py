from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class RunCommand(Command):
    """
    Executes a player-created NexusScript module.
    """
    def __init__(self, player_service):
        super().__init__("run", "Executes a player-created NexusScript module.", "run my_brute_force_v1 ($server_ip)")
        self.player_service = player_service

    def execute(self, player, args):
        if not args:
            raise CommandError("Usage: run <module_name> [args...]")

        module_name = args[0]
        module_args = args[1:]

        # In a real implementation, you would load the module from the player's
        # virtual file system and execute it using the NexusScript interpreter.

        return CommandResult(success=True, output=f"Executing module {module_name} with args: {module_args}")