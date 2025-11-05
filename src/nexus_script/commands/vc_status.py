from ...services.command_service import Command, CommandResult

class VCStatusCommand(Command):
    """
    Displays the current status of the virtual computer.
    """
    def __init__(self):
        super().__init__("vc.status", "Displays the current status of the virtual computer.", "vc.status")

    def execute(self, player, args):
        vc = player.virtual_computer
        output = "VC HARDWARE STATUS:\n"
        output += f"CPU Load: [ {vc.cpu_load}% ]\n"
        output += f"RAM Usage: [ {vc.ram_in_use} / {vc.get_max_ram()} MB ]\n\n"
        output += "ACTIVE PROCESSES:\n"
        output += "PID   NAME            CPU   RAM\n"
        for pid, process in vc.active_processes.items():
            output += f"{pid:<5} {process['name']:<15} {process['cpu']:<5} {process['ram']:<5}\n"

        return CommandResult(success=True, output=output)
