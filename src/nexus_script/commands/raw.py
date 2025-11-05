from ...services.command_service import Command, CommandResult
from ...core.exceptions import CommandError

class RawCommand(Command):
    """
    Allows sending custom, low-level data packets.
    """
    def __init__(self, player_service):
        super().__init__("raw", "Allows sending custom, low-level data packets.", "raw send $target_ip $data_packet")
        self.player_service = player_service

    def execute(self, player, args):
        if len(args) < 2:
            raise CommandError("Usage: raw send <target_ip> <data_packet>")

        target_ip = args[0]
        data_packet = " ".join(args[1:])

        # In a real implementation, you would bypass the high-level
        # Service_Object methods and inject raw data into the virtual
        # network stack.

        return CommandResult(success=True, output=f"Sending raw data packet to {target_ip}: {data_packet}")