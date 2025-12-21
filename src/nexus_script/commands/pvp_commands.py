from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class InjectCommand(Command):
    """
    Injects a virus to increase opponent's heat.
    """
    def __init__(self, player_service):
        super().__init__("inject", "Injects a virus to overheat opponent CPU.", "inject <target_player>")
        self.player_service = player_service
        self.heat_cost = 30.0
        self.min_level = 3

    def execute(self, player, args, context=None):
        if len(args) != 1:
            return CommandResult(success=False, error="Usage: inject <target_player>")

        target_name = args[0]
        target = self.player_service.get_player_by_name(target_name)

        if not target:
            return CommandResult(success=False, error=f"Target {target_name} not found.")

        # Defense check could go here (e.g. firewall tier)

        # Attack: Add 30 heat to target
        target.virtual_computer.add_heat(30.0)
        self.player_service.repository.save(target)

        return CommandResult(success=True, output=f"Virus injected into {target_name}. Heat increasing!", animation_type="HACKING_MATRIX")

class SiphonCommand(Command):
    """
    Steals credits from opponent.
    """
    def __init__(self, player_service):
        super().__init__("siphon", "Steal credits from opponent.", "siphon <target_player>")
        self.player_service = player_service
        self.heat_cost = 20.0
        self.min_level = 5

    def execute(self, player, args, context=None):
        if len(args) != 1:
            return CommandResult(success=False, error="Usage: siphon <target_player>")

        target_name = args[0]
        target = self.player_service.get_player_by_name(target_name)

        if not target:
            return CommandResult(success=False, error=f"Target {target_name} not found.")

        amount = 100 # Flat amount for now
        if target.stats.credits < amount:
            amount = target.stats.credits

        if amount <= 0:
             return CommandResult(success=False, error=f"{target_name} has no credits to steal.")

        # Transfer
        self.player_service.update_credits(target, -amount, f"Stolen by {player.name}")
        self.player_service.update_credits(player, amount, f"Stolen from {target_name}")

        return CommandResult(success=True, output=f"Siphoned {amount} credits from {target_name}.", animation_type="SUCCESS_UNLOCK")
