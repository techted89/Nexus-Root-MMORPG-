"""
Command execution service
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from ..models.player import Player
from ..core.events import EventBus, Event, GameEvents
from ..core.exceptions import CommandNotFoundError, InsufficientResourcesError, ScriptExecutionError, CommandError
from ..core.logger import NexusLogger

class CommandResult:
    """Result of command execution"""
    def __init__(self, success: bool, output: str = "", error: str = "", data: Dict[str, Any] = None):
        self.success = success
        self.output = output
        self.error = error
        self.data = data or {}
        self.execution_time_ms: float = 0

class Command(ABC):
    """Abstract base class for commands"""
    
    def __init__(self, name: str, description: str, syntax: str):
        self.name = name
        self.description = description
        self.syntax = syntax
        self.requires_vip = False
        self.min_level = 1
        self.resource_cost = 0
    
    @abstractmethod
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        """Execute the command"""
        pass
    
    def can_execute(self, player: Player) -> tuple[bool, str]:
        """Check if player can execute this command"""
        if not player.knowledge_map.is_command_available(self.name):
            return False, f"Command '{self.name}' is not available. Check your K-Map."
        
        if player.stats.level < self.min_level:
            return False, f"Command requires level {self.min_level}"
        
        if self.requires_vip and not player.is_vip:
            return False, f"Command '{self.name}' requires VIP access"
        
        if self.resource_cost > 0 and not player.can_afford(self.resource_cost):
            return False, f"Command costs {self.resource_cost} credits"
        
        return True, "OK"

from ..nexus_script.commands.dos_attack import DOSAttackCommand
from ..nexus_script.commands.set import SetCommand
from ..nexus_script.commands.run import RunCommand
from ..nexus_script.commands.pivot import PivotCommand
from ..nexus_script.commands.thread_spawn import ThreadSpawnCommand
from ..nexus_script.commands.raw import RawCommand
from ..nexus_script.commands.auto_defend import AutoDefendCommand

class LsCommand(Command):
    """List directory contents command"""
    
    def __init__(self):
        super().__init__("ls", "List directory contents", "ls [directory]")
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        # Simulated file system
        files = ["data.txt", "log.txt", "config.cfg", "mission_brief.md"]
        
        if args and args[0] == "-la":
            output = "total 4\n"
            output += "drwxr-xr-x  2 nexus nexus  4096 Oct 17 12:00 .\n"
            output += "drwxr-xr-x  3 nexus nexus  4096 Oct 17 11:00 ..\n"
            for file in files:
                output += f"-rw-r--r--  1 nexus nexus  1024 Oct 17 12:00 {file}\n"
        else:
            output = "  ".join(files)
        
        return CommandResult(True, output, data={"files": files})

class CatCommand(Command):
    """Display file contents command"""
    
    def __init__(self):
        super().__init__("cat", "Display file contents", "cat <filename>")
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: cat <filename>")
        
        filename = args[0]
        
        # Simulated file contents
        file_contents = {
            "data.txt": "target_ip=192.168.1.100\nport=22\nservice=ssh",
            "log.txt": "Connection established\nScanning ports...\nVulnerability found\nCMD_DECLARE: scan",
            "config.cfg": "timeout=30\nretries=3\nverbose=true",
            "mission_brief.md": "# Mission: Network Reconnaissance\nScan the target network and identify vulnerabilities."
        }
        
        if filename not in file_contents:
            return CommandResult(False, error=f"cat: {filename}: No such file or directory")
        
        content = file_contents[filename]

        # Scan for knowledge fragments
        unlocked_command = player.knowledge_map.scan_file_for_fragment(content)

        output = content
        if unlocked_command:
            output += f"\n\n[Knowledge fragment for '{unlocked_command}' discovered!]"

        return CommandResult(True, output, data={"filename": filename})

class ScanCommand(Command):
    """Network scan command"""
    
    def __init__(self):
        super().__init__("scan", "Scan network targets", "scan <target>")
        self.min_level = 2
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: scan <target>")
        
        target = args[0]
        
        # Simulate scan delay based on CPU tier
        scan_time = 3.0 * player.virtual_computer.cpu.get_speed_multiplier()
        if not player.is_vip:
            time.sleep(scan_time)
        
        # Simulated scan results
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
            }
        )

class HashcrackCommand(Command):
    """Hash cracking command"""
    
    def __init__(self):
        super().__init__("hashcrack", "Crack password hashes", "hashcrack <hash>")
        self.min_level = 3
        self.resource_cost = 10
    
    def execute(self, player: Player, args: List[str], context: Dict[str, Any] = None) -> CommandResult:
        if not args:
            return CommandResult(False, error="Usage: hashcrack <hash>")
        
        hash_value = args[0]
        
        # Simulate cracking time based on CPU tier
        crack_time = 5.0 * player.virtual_computer.cpu.get_speed_multiplier()
        
        output = f"Cracking hash: {hash_value}\n"
        if player.is_vip:
            output += "Using quantum-enhanced algorithms...\n"
        else:
            output += f"Estimated time: {crack_time:.1f}s\n"
            time.sleep(crack_time)
        
        # Simulated password result
        password = "password123"
        output += f"Password found: {password}"
        
        return CommandResult(
            True,
            output,
            data={
                "hash": hash_value,
                "password": password,
                "crack_time": crack_time
            }
        )

class CommandService:
    """Service for managing command execution"""
    
    def __init__(self, event_bus: EventBus = None, player_service = None):
        self.event_bus = event_bus or EventBus()
        self.player_service = player_service
        self.logger = NexusLogger.get_logger("command_service")
        self.commands: Dict[str, Command] = {}
        self.execution_context: Dict[str, Any] = {}
        
        # Register built-in commands
        self._register_builtin_commands()
    
    def _register_builtin_commands(self):
        """Register built-in commands"""
        commands = [
            SetCommand(self.player_service),
            LsCommand(),
            CatCommand(),
            ScanCommand(),
            HashcrackCommand(),
            DOSAttackCommand(self.player_service),
            RunCommand(self.player_service),
            PivotCommand(self.player_service),
            ThreadSpawnCommand(self.player_service),
            RawCommand(self.player_service),
            AutoDefendCommand(self.player_service),
        ]
        
        for command in commands:
            self.register_command(command)
    
    def register_command(self, command: Command):
        """Register a new command"""
        self.commands[command.name] = command
        self.logger.debug(f"Registered command: {command.name}")
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get command by name"""
        return self.commands.get(name)
    
    def get_available_commands(self, player: Player) -> List[Dict[str, Any]]:
        """Get list of available commands for player"""
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
                "resource_cost": command.resource_cost
            })
        
        return available
    
    def execute_command(self, player: Player, command_line: str) -> CommandResult:
        """Execute a command"""
        start_time = time.time()
        
        # Parse command
        parts = command_line.strip().split()
        if not parts:
            return CommandResult(False, error="No command specified")
        
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            # Check if player's CPU is locked
            if player.cpu_locked_until and player.cpu_locked_until > datetime.now():
                raise CommandError(f"CPU is locked. Time remaining: {player.cpu_locked_until - datetime.now()}")

            # Find command
            command = self.get_command(command_name)
            if not command:
                raise CommandNotFoundError(f"Unknown command: {command_name}")
            
            # Check permissions
            can_execute, reason = command.can_execute(player)
            if not can_execute:
                return CommandResult(False, error=reason)
            
            # Charge resources if needed
            if command.resource_cost > 0:
                if not player.can_afford(command.resource_cost):
                    raise InsufficientResourcesError(f"Command costs {command.resource_cost} credits")
                player.update_credits(-command.resource_cost)
            
            # Execute command
            result = command.execute(player, args, self.execution_context.copy())
            
            # Calculate execution time
            end_time = time.time()
            result.execution_time_ms = (end_time - start_time) * 1000
            
            # Update player stats
            player.stats.total_commands_executed += 1
            player.virtual_computer.total_commands_processed += 1
            
            # Publish event
            self.event_bus.publish(Event(
                GameEvents.COMMAND_EXECUTED,
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "command": command_name,
                    "args": args,
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms
                },
                source="command_service"
            ))
            
            self.logger.info(f"Command executed: {player.name} -> {command_name} ({'SUCCESS' if result.success else 'FAILED'})")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            error_result = CommandResult(False, error=str(e))
            error_result.execution_time_ms = execution_time_ms
            
            # Log error
            self.logger.error(f"Command execution error: {player.name} -> {command_line} -> {str(e)}")
            
            # Publish error event
            self.event_bus.publish(Event(
                GameEvents.COMMAND_EXECUTED,
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "command": command_name,
                    "args": args,
                    "success": False,
                    "error": str(e),
                    "execution_time_ms": execution_time_ms
                },
                source="command_service"
            ))
            
            return error_result
    
    def get_command_help(self, command_name: str = None) -> str:
        """Get help for commands"""
        if command_name:
            command = self.get_command(command_name)
            if not command:
                return f"Unknown command: {command_name}"
            
            return f"{command.name}: {command.description}\nSyntax: {command.syntax}"
        
        # List all commands
        output = "Available commands:\n"
        for command in sorted(self.commands.values(), key=lambda c: c.name):
            output += f"  {command.name:<15} - {command.description}\n"
        
        return output