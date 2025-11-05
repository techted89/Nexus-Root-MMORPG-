from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class SetCommand(Command):
    """
    Declare a variable or instantiate a new object.
    """
    def __init__(self, player_service):
        super().__init__("set", "Declare a variable or instantiate a new object.", "set $var = [value]")
        self.player_service = player_service

    def execute(self, player, args):
        if len(args) < 3 or args[1] != "=":
            raise CommandError("Usage: set $var = [value]")

        var_name = args[0]
        value = " ".join(args[2:])

        if not var_name.startswith("$"):
            raise CommandError("Variable name must start with $")

        # In a real implementation, you would store the variable in the player's session
        # or virtual computer state.

        return CommandResult(success=True, output=f"Variable {var_name} set to {value}")