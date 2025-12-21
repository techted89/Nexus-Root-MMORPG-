"""
Command execution service
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.player import Player
from ..core.events import EventBus, Event, GameEvents
from ..core.exceptions import CommandNotFoundError, InsufficientResourcesError, ScriptExecutionError, CommandError
from ..core.logger import NexusLogger
from ..core.command import Command, CommandResult
from ..nexus_script.commands.basic_commands import WhoamiCommand, EchoCommand, DateCommand
from ..nexus_script.commands.dos_attack import DOSAttackCommand
from ..nexus_script.commands.pvp_commands import InjectCommand, SiphonCommand
from ..nexus_script.commands.item_commands import InventoryCommand, EquipCommand, UseCommand
from ..commands.jobs_command import JobsCommand
from ..services.job_service import JobService

class SetCommand(Command):
    """Set variable command"""
    
    def __init__(self):
        super().__init__("set", "Set a variable value", "set <variable> = <value>")
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if len(args) < 3 or args[1] != "=":
            return CommandResult(False, error="Usage: set <variable> = <value>", animation_type="ERROR_SHAKE")
        
        var_name = args[0]
        value = " ".join(args[2:])
        
        if context is None:
            context = {}
        context[var_name] = value
        
        return CommandResult(True, f"Set {var_name} = {value}", data={"variable": var_name, "value": value}, animation_type="TEXT_ONLY")

class LsCommand(Command):
    """List directory contents command"""
    
    def __init__(self):
        super().__init__("ls", "List directory contents", "ls [directory]")
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        files = ["data.txt", "log.txt", "config.cfg", "mission_brief.md"]
        
        if args and args[0] == "-la":
            output = "total 4\n"
            output += "drwxr-xr-x  2 nexus nexus  4096 Oct 17 12:00 .\n"
            output += "drwxr-xr-x  3 nexus nexus  4096 Oct 17 11:00 ..\n"
            for file in files:
                output += f"-rw-r--r--  1 nexus nexus  1024 Oct 17 12:00 {file}\n"
        else:
            output = "  ".join(files)
        
        return CommandResult(True, output, data={"files": files}, animation_type="TEXT_ONLY")

class CatCommand(Command):
    """Display file contents command"""
    
    def __init__(self):
        super().__init__("cat", "Display file contents", "cat <filename>")
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: cat <filename>", animation_type="ERROR_SHAKE")
        
        filename = args[0]
        
        file_contents = {
            "data.txt": "target_ip=192.168.1.100\nport=22\nservice=ssh",
            "log.txt": "Connection established\nScanning ports...\nVulnerability found",
            "config.cfg": "timeout=30\nretries=3\nverbose=true",
            "mission_brief.md": "# Mission: Network Reconnaissance\nScan the target network and identify vulnerabilities."
        }
        
        if filename not in file_contents:
            return CommandResult(False, error=f"cat: {filename}: No such file or directory", animation_type="ERROR_SHAKE")
        
        return CommandResult(True, file_contents[filename], data={"filename": filename}, animation_type="TEXT_ONLY")

class ScanCommand(Command):
    """Network scan command"""
    
    def __init__(self):
        super().__init__("scan", "Scan network targets", "scan <target>")
        self.min_level = 2
        self.heat_cost = 15.0
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: scan <target>", animation_type="ERROR_SHAKE")
        
        target = args[0]
        
        scan_time = 3.0 * player.virtual_computer.get_cpu_speed()
        if not player.is_vip:
            time.sleep(scan_time)
        
        ports = [22, 80, 443, 8080]
        services = ["ssh", "http", "https", "http-proxy"]
        
        output = f"Scanning {target}...\n"
        output += "PORT     STATE    SERVICE\n"
        for port, service in zip(ports, services):
            output += f"{port}/tcp  open     {service}\n"
        
        return CommandResult(
            True,
            output,
            data={
                "target": target,
                "open_ports": ports,
                "services": services,
                "scan_time": scan_time
            },
            animation_type="SCANNING_RADAR"
        )

class HashcrackCommand(Command):
    """Hash cracking command"""
    
    def __init__(self):
        super().__init__("hashcrack", "Crack password hashes", "hashcrack <hash>")
        self.min_level = 3
        self.resource_cost = 10
        self.heat_cost = 25.0
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: hashcrack <hash>", animation_type="ERROR_SHAKE")
        
        hash_value = args[0]
        
        crack_time = 5.0 * player.virtual_computer.get_cpu_speed()
        
        output = f"Cracking hash: {hash_value}\n"
        if player.is_vip:
            output += "Using quantum-enhanced algorithms...\n"
        else:
            output += f"Estimated time: {crack_time:.1f}s\n"
            time.sleep(crack_time)
        
        password = "password123"
        output += f"Password found: {password}"
        
        return CommandResult(
            True,
            output,
            data={
                "hash": hash_value,
                "password": password,
                "crack_time": crack_time
            },
            animation_type="HACKING_MATRIX"
        )

class CommandService:
    """Service for managing command execution"""
    
    def __init__(self, event_bus: EventBus = None, player_service = None):
        self.event_bus = event_bus or EventBus()
        self.player_service = player_service
        self.job_service = JobService(event_bus=self.event_bus)
        self.logger = NexusLogger.get_logger("command_service")
        self.commands: Dict[str, Command] = {}
        self.execution_context: Dict[str, Any] = {}
        
        self._register_builtin_commands()
    
    def _register_builtin_commands(self):
        """Register built-in commands"""
        commands = [
            SetCommand(),
            LsCommand(),
            CatCommand(),
            ScanCommand(),
            HashcrackCommand(),
            DOSAttackCommand(self.player_service),
            WhoamiCommand(),
            EchoCommand(),
            DateCommand(),
            InjectCommand(self.player_service),
            SiphonCommand(self.player_service),
            InventoryCommand(self.player_service),
            EquipCommand(self.player_service),
            UseCommand(self.player_service)
            JobsCommand(self.job_service)
        ]
        
        for command in commands:
            self.register_command(command)
    
    def register_command(self, command: Command):
        self.commands[command.name] = command
        self.logger.debug(f"Registered command: {command.name}")
    
    def get_command(self, name: str) -> Optional[Command]:
        return self.commands.get(name)
    
    def get_available_commands(self, player: Player) -> List[Dict[str, Any]]:
        available = []
        for command in self.commands.values():
            can_execute, reason = command.can_execute(player)
            available.append({
                "name": command.name,
                "description": command.description,
                "syntax": command.syntax,
                "available": can_execute,
                "reason": reason if not can_execute else None,
                "requires_vip": command.requires_vip,
                "min_level": command.min_level,
                "resource_cost": command.resource_cost,
                "heat_cost": command.heat_cost
            })
        return available
    
    def execute_command(self, player: Player, command_line: str) -> CommandResult:
        """Execute a command"""
        start_time = time.time()
        
        parts = command_line.strip().split()
        if not parts:
            return CommandResult(False, error="No command specified", animation_type="ERROR_SHAKE")
        
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            if player.cpu_locked_until and player.cpu_locked_until > datetime.now():
                raise CommandError(f"CPU is locked. Time remaining: {player.cpu_locked_until - datetime.now()}")

            command = self.get_command(command_name)
            if not command:
                raise CommandNotFoundError(f"Unknown command: {command_name}")
            
            # Check Heat
            if player.virtual_computer.is_overheated():
                return CommandResult(False, error="System Overheated! Wait for cooldown.", animation_type="ERROR_SHAKE")

            can_execute, reason = command.can_execute(player)
            if not can_execute:
                return CommandResult(False, error=reason, animation_type="ERROR_SHAKE")
            
            if command.resource_cost > 0:
                if not player.can_afford(command.resource_cost):
                    raise InsufficientResourcesError(f"Command costs {command.resource_cost} credits")
                player.update_credits(-command.resource_cost)
            
            result = command.execute(player, args, self.execution_context.copy())
            
            # Apply Heat Cost
            player.virtual_computer.add_heat(command.heat_cost)

            end_time = time.time()
            result.execution_time_ms = (end_time - start_time) * 1000
            
            player.stats.total_commands_executed += 1
            player.virtual_computer.total_commands_processed += 1
            
            self.event_bus.publish(Event(
                GameEvents.COMMAND_EXECUTED,
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "command": command_name,
                    "args": args,
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms,
                    "animation_type": result.animation_type
                },
                source="command_service"
            ))
            
            self.logger.info(f"Command executed: {player.name} -> {command_name} ({'SUCCESS' if result.success else 'FAILED'})")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            error_result = CommandResult(False, error=str(e), animation_type="ERROR_SHAKE")
            error_result.execution_time_ms = execution_time_ms
            
            self.logger.error(f"Command execution error: {player.name} -> {command_line} -> {str(e)}")
            
            self.event_bus.publish(Event(
                GameEvents.COMMAND_EXECUTED,
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "command": command_name,
                    "args": args,
                    "success": False,
                    "error": str(e),
                    "execution_time_ms": execution_time_ms,
                    "animation_type": "ERROR_SHAKE"
                },
                source="command_service"
            ))
            
            return error_result
    
    def get_command_help(self, command_name: str = None) -> str:
        if command_name:
            command = self.get_command(command_name)
            if not command:
                return f"Unknown command: {command_name}"
            return f"{command.name}: {command.description}\nSyntax: {command.syntax}"
        
        output = "Available commands:\n"
        for command in sorted(self.commands.values(), key=lambda c: c.name):
            output += f"  {command.name:<15} - {command.description}\n"
        return output
