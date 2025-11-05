from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class PivotCommand(Command):
    """
    Routes an attack through a compromised asset to reach an internal network.
    """
    def __init__(self, player_service):
        super().__init__("pivot", "Routes an attack through a compromised asset.", "pivot $compromised_server scan 10 10 0 0")
        self.player_service = player_service

    def execute(self, player, args):
        if len(args) < 2:
            raise CommandError("Usage: pivot <compromised_server> <command>")

        compromised_server = args[0]
        command_to_run = " ".join(args[1:])

        # In a real implementation, you would verify that the player has control
        # over the compromised server and then execute the command from that
        # server's context.

        return CommandResult(success=True, output=f"Pivoting through {compromised_server} to run: {command_to_run}")