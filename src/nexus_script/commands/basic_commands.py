from ...core.command import Command, CommandResult
from ...models.player import Player
from typing import List, Dict, Any
import datetime

class WhoamiCommand(Command):
    """Display current user info"""
    def __init__(self):
        super().__init__("whoami", "Display current user info", "whoami")

    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        info = f"User: {player.name}\n"
        info += f"Level: {player.stats.level}\n"
        info += f"Wallet: {player.wallet_address}\n"
        info += f"VIP: {player.is_vip}"
        return CommandResult(True, info)

class EchoCommand(Command):
    """Print arguments to output"""
    def __init__(self):
        super().__init__("echo", "Display a line of text", "echo [text]")

    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        text = " ".join(args)
        return CommandResult(True, text)

class DateCommand(Command):
    """Display current system date and time"""
    def __init__(self):
        super().__init__("date", "Display current date/time", "date")

    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return CommandResult(True, now)
