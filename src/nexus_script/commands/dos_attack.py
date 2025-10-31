from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class DOSAttackCommand(Command):
    """
    Temporarily locks an opponent's CPU in PvP game modes.
    """
    def __init__(self, player_service):
        super().__init__("dos_attack", "Temporarily locks an opponent's CPU.", "dos_attack <target_player>")
        self.player_service = player_service

    def execute(self, player, args):
        if len(args) != 1:
            raise CommandError("Usage: dos_attack <target_player>")

        target_player_name = args[0]
        target_player = self.player_service.get_player_by_name(target_player_name)

        if not target_player:
            raise CommandError(f"Player not found: {target_player_name}")

        # In a real implementation, you would check if the players are in a PvP game mode
        # and if the target is a valid opponent.

        # Lock the target's CPU for 30 seconds
        self.player_service.lock_cpu(target_player, 30)

        return CommandResult(success=True, output=f"DoS attack launched against {target_player_name}. Their CPU will be locked for 30 seconds.")