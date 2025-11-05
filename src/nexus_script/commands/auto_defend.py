from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class AutoDefendCommand(Command):
    """
    Enables or disables the automated defense system for VIP players.
    """
    def __init__(self, player_service):
        super().__init__("vc.auto_defend", "Enables or disables the automated defense system.", "vc.auto_defend on|off")
        self.player_service = player_service
        self.requires_vip = True

    def execute(self, player, args):
        if not args or args[0] not in ["on", "off"]:
            raise CommandError("Usage: vc.auto_defend on|off")

        status = args[0]
        player.settings["auto_defend"] = status == "on"

        return CommandResult(success=True, output=f"Automated defense system turned {status}.")