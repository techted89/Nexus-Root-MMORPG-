"""
Main entry point for the redesigned Nexus Root MMORPG
"""

import sys
import argparse
from .shell_redesigned import NexusShellRedesigned
from .api.game_api import GameAPI
from .core.config import NexusConfig
from .core.logger import NexusLogger

def create_sample_config():
    """Create a sample configuration file"""
    config = NexusConfig()
    config.save_to_file("config.json")
    print("Created sample configuration file: config.json")

def run_shell(args):
    """Run the interactive shell"""
    try:
        # Load configuration
        if args.config:
            config = NexusConfig.load_from_file(args.config)
        else:
            config = NexusConfig.load_from_file()
        
        # Override with command line arguments
        if args.debug:
            config.server.debug = True
            config.log_level = "DEBUG"
        
        # Create and start shell
        shell = NexusShellRedesigned(config)
        shell.start(args.player)
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def run_api_server(args):
    """Run the API server"""
    try:
        import asyncio
        from .server.web_server import WebServer
        from .server.websocket_server import WebSocketServer

        # Load configuration
        if args.config:
            config = NexusConfig.load_from_file(args.config)
        else:
            config = NexusConfig.load_from_file()

        # Override with command line arguments
        if args.host:
            config.server.host = args.host
        if args.port:
            config.server.port = args.port
        if args.debug:
            config.server.debug = True
            config.log_level = "DEBUG"

        async def main():
            game_api = GameAPI(config)

            # Create and start web server in a separate thread
            web_server = WebServer(config)
            web_server_thread = asyncio.to_thread(web_server.run)

            # Create and start WebSocket server
            ws_server = WebSocketServer(config.server.host, config.server.port + 1, game_api)
            await ws_server.start()

            await web_server_thread

        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {str(e)}")
        sys.exit(1)

def run_tests():
    """Run the test suite"""
    try:
        import pytest
        import os
        
        # Change to project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_dir)
        
        # Run tests
        exit_code = pytest.main(["-v", "tests/"])
        sys.exit(exit_code)
        
    except ImportError:
        print("Error: pytest not installed. Install with: pip install pytest")
        sys.exit(1)
    except Exception as e:
        print(f"Test error: {str(e)}")
        sys.exit(1)

def show_status(args):
    """Show server status and statistics"""
    try:
        # Load configuration
        if args.config:
            config = NexusConfig.load_from_file(args.config)
        else:
            config = NexusConfig.load_from_file()
        
        # Create API instance
        api = GameAPI(config)
        
        # Get statistics
        result = api.get_server_statistics()
        
        if result["success"]:
            stats = result["data"]
            print("Nexus Root Server Status")
            print("=" * 30)
            print(f"Total Players: {stats['total_players']}")
            print(f"Online Players: {stats['online_players']}")
            print(f"Total Missions: {stats['total_missions']}")
            print()
            print("Mission Statistics:")
            mission_stats = stats['mission_statistics']
            for status, count in mission_stats.get('by_status', {}).items():
                print(f"  {status.title()}: {count}")
            print(f"  Completion Rate: {mission_stats.get('completion_rate', 0):.1f}%")
        else:
            print(f"Error getting status: {result['error']}")
            
        api.shutdown()
        
    except Exception as e:
        print(f"Status error: {str(e)}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Nexus Root MMORPG - The Hacking Strategy Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s shell                    # Run interactive shell
  %(prog)s shell --player Alice     # Login as specific player
  %(prog)s server                   # Run API server
  %(prog)s server --port 8080       # Run server on custom port
  %(prog)s status                   # Show server statistics
  %(prog)s test                     # Run test suite
  %(prog)s config                   # Create sample config file
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shell command
    shell_parser = subparsers.add_parser("shell", help="Run interactive shell")
    shell_parser.add_argument("--player", "-p", help="Player name to login as")
    shell_parser.add_argument("--config", "-c", help="Configuration file path")
    shell_parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run API server")
    server_parser.add_argument("--host", help="Server host")
    server_parser.add_argument("--port", type=int, help="Server port")
    server_parser.add_argument("--config", "-c", help="Configuration file path")
    server_parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show server status")
    status_parser.add_argument("--config", "-c", help="Configuration file path")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run test suite")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Create sample configuration file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "shell" or args.command is None:
        run_shell(args)
    elif args.command == "server":
        run_api_server(args)
    elif args.command == "status":
        show_status(args)
    elif args.command == "test":
        run_tests()
    elif args.command == "config":
        create_sample_config()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()