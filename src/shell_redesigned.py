"""
Redesigned shell interface using the new architecture
"""

import sys
from typing import Optional
from .api.game_api import GameAPI
from .nexus_script.themes import THEMES
from .core.config import NexusConfig
from .core.logger import NexusLogger
from .core.exceptions import NexusException

class NexusShellRedesigned:
    """Redesigned Nexus Shell using the new architecture"""
    
    def __init__(self, config: NexusConfig = None):
        """Initialize the redesigned shell"""
        self.config = config or NexusConfig.load_from_file()
        
        # Initialize logging
        NexusLogger.initialize(self.config.log_level, self.config.log_file)
        self.logger = NexusLogger.get_logger("shell")
        
        # Initialize game API
        self.game_api = GameAPI(self.config)
        
        # Shell state
        self.current_player = None
        self.session_id = None
        self.running = True
        
        self.logger.info("Nexus Shell initialized")
    
    def start(self, player_name: str = None):
        """Start the shell"""
        print("Welcome to Nexus Root MMORPG")
        print("=" * 40)
        
        # Handle player authentication
        if player_name:
            self.authenticate_player(player_name)
        else:
            self.handle_login()
        
        if self.current_player:
            self.main_loop()
        else:
            print("Authentication failed. Exiting.")
    
    def handle_login(self):
        """Handle player login or creation"""
        while not self.current_player:
            print("\n1. Login with existing player")
            print("2. Create new player")
            print("3. Exit")
            
            choice = input("Choose option (1-3): ").strip()
            
            if choice == "1":
                name = input("Enter player name: ").strip()
                if name:
                    self.authenticate_player(name)
            
            elif choice == "2":
                self.create_new_player()
            
            elif choice == "3":
                self.running = False
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    def create_new_player(self):
        """Create a new player"""
        print("\nCreate New Player")
        print("-" * 20)
        
        name = input("Enter player name (2-20 characters): ").strip()
        if not name:
            return
        
        is_vip = input("VIP player? (y/n): ").strip().lower() == 'y'
        
        result = self.game_api.create_player(name, is_vip, self.session_id)
        
        if result["success"]:
            print(f"\n✓ {result['message']}")
            self.authenticate_player(name)
        else:
            print(f"\n✗ Error: {result['error']}")
    
    def authenticate_player(self, name: str):
        """Authenticate a player"""
        result = self.game_api.authenticate_player(name, self.session_id)
        
        if result["success"]:
            self.current_player = name
            player_data = result["data"]
            
            print(f"\n✓ Welcome back, {name}!")
            print(f"Level: {player_data['level']} | Credits: {player_data['credits']} | XP: {player_data['experience']}")
            
            # Check passive mining
            mining_result = self.game_api.check_passive_mining(name)
            if mining_result["success"] and "credits_earned" in mining_result.get("data", {}):
                print(f"✓ Passive mining complete! Earned {mining_result['data']['credits_earned']} credits.")
            
            self.logger.info(f"Player authenticated: {name}")
        else:
            print(f"\n✗ Authentication failed: {result['error']}")
    
    def main_loop(self):
        """Main shell loop"""
        print(f"\nNexus Shell ready. Type 'help' for commands or 'exit' to quit.")
        
        while self.running and self.current_player:
            try:
                # Get current player data for prompt
                player_result = self.game_api.get_player_by_name(self.current_player)
                if not player_result["success"]:
                    print("Error: Lost connection to player data")
                    break
                
                player_data = player_result["data"]
                theme = THEMES.get(player_data.get("theme", "default"), THEMES["default"])
                
                # Create prompt
                prompt = (theme["prompt"] + 
                         f"{self.current_player}@nexus-root> " + 
                         theme["reset"])
                
                # Get input
                try:
                    command_line = input(prompt).strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n")
                    self.handle_exit()
                    break
                
                if not command_line:
                    continue
                
                # Handle built-in shell commands
                if self.handle_builtin_command(command_line):
                    continue
                
                # Execute game command
                self.execute_game_command(command_line)
                
            except Exception as e:
                self.logger.error(f"Shell error: {str(e)}")
                print(f"Shell error: {str(e)}")
    
    def handle_builtin_command(self, command_line: str) -> bool:
        """Handle built-in shell commands"""
        parts = command_line.split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "exit" or cmd == "quit":
            self.handle_exit()
            return True
        
        elif cmd == "help":
            self.show_help(args[0] if args else None)
            return True
        
        elif cmd == "status":
            self.show_status()
            return True
        
        elif cmd == "missions":
            self.show_missions()
            return True
        
        elif cmd == "hardware" or cmd == "shop":
            self.show_hardware_shop()
            return True
        
        elif cmd == "buy":
            if args:
                self.buy_hardware(args[0])
            else:
                print("Usage: buy <component>")
            return True
        
        elif cmd == "leaderboard":
            category = args[0] if args else "level"
            self.show_leaderboard(category)
            return True
        
        elif cmd == "theme":
            if args:
                self.change_theme(args[0])
            else:
                self.list_themes()
            return True
        
        elif cmd == "mine":
            if args:
                try:
                    hours = int(args[0])
                    self.start_mining(hours)
                except ValueError:
                    print("Usage: mine <hours>")
            else:
                print("Usage: mine <hours>")
            return True
        
        elif cmd == "mission":
            if len(args) >= 2:
                action = args[0]
                mission_id = args[1]
                if action == "start":
                    self.start_mission(mission_id)
                elif action == "abandon":
                    self.abandon_mission(mission_id)
                else:
                    print("Usage: mission start|abandon <mission_id>")
            else:
                print("Usage: mission start|abandon <mission_id>")
            return True
        
        return False
    
    def execute_game_command(self, command_line: str):
        """Execute a game command through the API"""
        result = self.game_api.execute_command(self.current_player, command_line)
        
        if result["success"]:
            if result["output"]:
                print(result["output"])
        else:
            if result["error"]:
                print(f"Error: {result['error']}")
        
        # Show execution time for VIP players or debug mode
        if self.config.server.debug and "execution_time_ms" in result:
            print(f"[DEBUG] Execution time: {result['execution_time_ms']:.2f}ms")
    
    def show_help(self, command: str = None):
        """Show help information"""
        if command:
            # Show help for specific command
            result = self.game_api.get_command_help(command)
            if result["success"]:
                print(result["data"])
        else:
            # Show general help
            print("Nexus Root Shell - Available Commands:")
            print("=" * 40)
            print("Built-in Shell Commands:")
            print("  help [command]    - Show help")
            print("  status           - Show player status")
            print("  missions         - Show available missions")
            print("  hardware/shop    - Show hardware shop")
            print("  buy <component>  - Buy hardware upgrade")
            print("  leaderboard      - Show leaderboard")
            print("  theme [name]     - Change or list themes")
            print("  mine <hours>     - Start passive mining")
            print("  mission start|abandon <id> - Manage missions")
            print("  exit/quit        - Exit shell")
            print()
            print("Game Commands:")
            
            # Get available game commands
            result = self.game_api.get_available_commands(self.current_player)
            if result["success"]:
                for cmd in result["data"]:
                    status = "✓" if cmd["available"] else "✗"
                    vip = " (VIP)" if cmd["requires_vip"] else ""
                    level = f" (L{cmd['min_level']})" if cmd["min_level"] > 1 else ""
                    cost = f" ({cmd['resource_cost']}C)" if cmd["resource_cost"] > 0 else ""
                    print(f"  {status} {cmd['name']:<12} - {cmd['description']}{vip}{level}{cost}")
    
    def show_status(self):
        """Show player status"""
        result = self.game_api.get_player_by_name(self.current_player)
        if not result["success"]:
            print("Error getting player status")
            return
        
        player = result["data"]
        
        print(f"Player: {player['name']}")
        print(f"Level: {player['level']} | XP: {player['experience']}")
        print(f"Credits: {player['credits']}")
        print(f"VIP: {'Yes' if player['is_vip'] else 'No'}")
        print()
        
        # Show hardware
        hardware_result = self.game_api.get_hardware_info(self.current_player)
        if hardware_result["success"]:
            hw = hardware_result["data"]
            print("Virtual Computer:")
            print(f"  CPU: Tier {hw['cpu']['tier']}")
            print(f"  RAM: Tier {hw['ram']['tier']} ({hw['ram']['max_threads']} threads)")
            print(f"  NIC: Tier {hw['nic']['tier']} ({hw['nic']['bandwidth_mbps']} Mbps)")
            print(f"  SSD: Tier {hw['ssd']['tier']} ({hw['ssd']['capacity_gb']} GB)")
        
        # Check mining status
        mining_result = self.game_api.check_passive_mining(self.current_player)
        if mining_result["success"]:
            print()
            print("Mining Status:")
            print(f"  {mining_result['message']}")
    
    def show_missions(self):
        """Show available and active missions"""
        print("Missions:")
        print("=" * 40)
        
        # Available missions
        result = self.game_api.get_available_missions(self.current_player)
        if result["success"] and result["data"]:
            print("Available Missions:")
            for mission in result["data"]:
                print(f"  [{mission['mission_id']}] {mission['name']}")
                print(f"    {mission['difficulty'].title()} - Type: {mission['type']}")
                print(f"    Objectives: {len(mission['objectives'])}")
                print()
        
        # Active missions
        result = self.game_api.get_active_missions(self.current_player)
        if result["success"] and result["data"]:
            print("Active Missions:")
            for mission in result["data"]:
                completed_objectives = sum(1 for obj in mission['objectives'] if obj['completed'])
                total_objectives = len(mission['objectives'])
                print(f"  [{mission['mission_id']}] {mission['name']}")
                print(f"    Progress: {completed_objectives}/{total_objectives} objectives complete")
                for obj in mission['objectives']:
                    status = "✓" if obj['completed'] else "○"
                    print(f"      {status} {obj['description']} ({obj['progress']})")
                print()
    
    def show_hardware_shop(self):
        """Show hardware shop"""
        result = self.game_api.get_hardware_info(self.current_player)
        if not result["success"]:
            print("Error getting hardware info")
            return
        
        hw = result["data"]
        
        print("Hardware Shop:")
        print("=" * 40)
        
        for component, info in hw.items():
            print(f"{component.upper()}:")
            print(f"  Current Tier: {info['tier']}")
            if info['can_upgrade']:
                print(f"  Upgrade Cost: {info['upgrade_cost']} credits")
                print(f"  Next Tier: {info['tier'] + 1}")
            else:
                print("  Max tier reached")
            print()
    
    def buy_hardware(self, component: str):
        """Buy hardware upgrade"""
        result = self.game_api.upgrade_hardware(self.current_player, component)
        
        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['error']}")
    
    def show_leaderboard(self, category: str = "level"):
        """Show leaderboard"""
        result = self.game_api.get_leaderboard(category, 10)
        
        if result["success"]:
            print(f"Leaderboard - {category.title()}:")
            print("=" * 40)
            
            for entry in result["data"]:
                vip = " (VIP)" if entry["is_vip"] else ""
                print(f"{entry['rank']:2}. {entry['name']:<15} "
                      f"L{entry['level']:2} | {entry['credits']:>6}C | "
                      f"{entry['missions_completed']:>3}M{vip}")
        else:
            print(f"Error: {result['error']}")
    
    def list_themes(self):
        """List available themes"""
        print("Available themes:")
        for theme_name in THEMES.keys():
            print(f"  {theme_name}")
    
    def change_theme(self, theme_name: str):
        """Change player theme"""
        if theme_name not in THEMES:
            print(f"Unknown theme: {theme_name}")
            self.list_themes()
            return
        
        # This would update player settings through the API
        print(f"Theme changed to: {theme_name}")
    
    def start_mining(self, hours: int):
        """Start passive mining"""
        result = self.game_api.start_passive_mining(self.current_player, hours)
        
        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['error']}")
    
    def start_mission(self, mission_id: str):
        """Start a mission"""
        result = self.game_api.start_mission(self.current_player, mission_id)
        
        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['error']}")
    
    def abandon_mission(self, mission_id: str):
        """Abandon a mission"""
        result = self.game_api.abandon_mission(self.current_player, mission_id)
        
        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['error']}")
    
    def handle_exit(self):
        """Handle shell exit"""
        if self.current_player:
            print(f"Goodbye, {self.current_player}!")
            
            # Logout player
            self.game_api.logout_player(self.current_player)
        
        self.running = False
        
        # Cleanup
        self.game_api.cleanup_old_data()
        self.game_api.shutdown()