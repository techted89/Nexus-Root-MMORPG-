import sys
import os
import json
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import NexusConfig
from src.api.game_api import GameAPI
from src.models.player import Player

async def create_snapshot():
    """Create a snapshot environment for testing/viewing"""
    print("--- Creating Build Snapshot ---")

    # Load config
    config = NexusConfig()

    # Use a specific snapshot DB file or the default?
    # Using the default from config so it works immediately with the server.
    db_path = config.database.database
    print(f"Target Database: {db_path}")

    # Initialize Game API (which inits DB)
    game_api = GameAPI(config)

    snapshot_user = "snapshot_user"

    # Check if user exists, if so, maybe reset?
    # For now, we'll try to create or update.

    existing_player = game_api.get_player_by_name(snapshot_user)
    if existing_player['success'] and existing_player['data']:
        print(f"Player {snapshot_user} exists. Updating stats...")
    else:
        print(f"Creating player {snapshot_user}...")
        game_api.create_player(snapshot_user, is_vip=True, session_id="snapshot_session")

    # Access services directly to manipulate state for "Snapshot" look
    player_service = game_api.player_service

    # Get the player object
    player = player_service.get_player_by_name(snapshot_user)
    if not player:
        print("Error: Could not retrieve player.")
        return

    print("Setting high-level stats...")
    player.level = 10  # Note: logic might overwrite this if exp doesn't match, but we force it here
    player.stats.level = 10 # Force stats object directly
    player.stats.credits = 50000
    player.stats.experience = 9000

    print("Unlocking commands...")
    # Simulate finding knowledge
    known_commands = ["ls", "cat", "ps", "kill", "connect", "scan", "hashcrack", "analyze", "exploit"]

    for cmd in known_commands:
        # 1. Ensure it's not locked
        if cmd in player.knowledge_map.locked_commands:
            player.knowledge_map.unlock_command(cmd)
            print(f"  Unlocked {cmd}")

        # 2. Integrate it (fully learned)
        if cmd not in player.knowledge_map.integrated_commands:
             player.knowledge_map.integrate_command(cmd)
             print(f"  Integrated {cmd}")

    print("Upgrading hardware...")
    # Max out some hardware
    # Corrected attribute access based on VirtualComputer model
    player.virtual_computer.cpu.tier = 5
    player.virtual_computer.ram.tier = 4
    player.virtual_computer.storage.tier = 3
    player.virtual_computer.network_card.tier = 5

    # Save changes
    # Corrected: repository is accessed via .repository, and method is .save()
    player_service.repository.save(player)

    print(f"Snapshot creation complete.")
    print(f"User: {snapshot_user}")
    print(f"Level: {player.stats.level}")
    print(f"Credits: {player.stats.credits}")
    print("-------------------------------")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_snapshot())
