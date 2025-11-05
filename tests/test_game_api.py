"""
Tests for game API
"""

import pytest
import tempfile
import os
from src.api.game_api import GameAPI
from src.core.config import NexusConfig

class TestGameAPI:
    """Test cases for GameAPI"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def config(self, temp_db):
        """Create test configuration"""
        config = NexusConfig()
        config.database.database = temp_db
        return config
    
    @pytest.fixture
    def game_api(self, config):
        """Create game API with test configuration"""
        return GameAPI(config)
    
    def test_create_player_api(self, game_api):
        """Test player creation through API"""
        result = game_api.create_player("TestPlayer", is_vip=False)
        
        assert result["success"] == True
        assert result["data"]["name"] == "TestPlayer"
        assert result["data"]["level"] == 1
        assert result["data"]["credits"] == 0
    
    def test_create_duplicate_player_api(self, game_api):
        """Test creating duplicate player through API"""
        game_api.create_player("TestPlayer")
        result = game_api.create_player("TestPlayer")
        
        assert result["success"] == False
        assert "already taken" in result["error"]
    
    def test_authenticate_player_api(self, game_api):
        """Test player authentication through API"""
        # Create player
        game_api.create_player("TestPlayer")
        
        # Authenticate
        result = game_api.authenticate_player("TestPlayer", "session123")
        
        assert result["success"] == True
        assert result["data"]["name"] == "TestPlayer"
    
    def test_authenticate_nonexistent_player(self, game_api):
        """Test authentication with nonexistent player"""
        result = game_api.authenticate_player("NonExistent", "session123")
        
        assert result["success"] == False
        assert "Invalid player name" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_command_api(self, game_api):
        """Test command execution through API"""
        # Create and authenticate player
        game_api.create_player("TestPlayer")
        game_api.authenticate_player("TestPlayer")
        
        # Execute command
        result = await game_api.execute_command("TestPlayer", "ls")
        
        assert result["success"] == True
        assert result["output"] is not None
        assert result["execution_time_ms"] >= 0
    
    @pytest.mark.asyncio
    async def test_execute_command_unknown_player(self, game_api):
        """Test command execution with unknown player"""
        result = await game_api.execute_command("UnknownPlayer", "ls")
        
        assert result["success"] == False
        assert "Player not found" in result["error"]
    
    def test_get_available_commands(self, game_api):
        """Test getting available commands"""
        # Create player
        game_api.create_player("TestPlayer")
        
        result = game_api.get_available_commands("TestPlayer")
        
        assert result["success"] == True
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0
        
        # Check command structure
        cmd = result["data"][0]
        assert "name" in cmd
        assert "description" in cmd
        assert "available" in cmd
    
    def test_get_available_missions(self, game_api):
        """Test getting available missions"""
        # Create player
        game_api.create_player("TestPlayer")
        
        result = game_api.get_available_missions("TestPlayer")
        
        assert result["success"] == True
        assert isinstance(result["data"], list)
        # Should have tutorial missions
        assert len(result["data"]) > 0
    
    def test_start_mission(self, game_api):
        """Test starting a mission"""
        # Create player
        game_api.create_player("TestPlayer")
        
        # Get available missions
        missions_result = game_api.get_available_missions("TestPlayer")
        if missions_result["data"]:
            mission_id = missions_result["data"][0]["mission_id"]
            
            # Start mission
            result = game_api.start_mission("TestPlayer", mission_id)
            
            assert result["success"] == True
            assert "started" in result["message"].lower()
    
    def test_upgrade_hardware_api(self, game_api):
        """Test hardware upgrade through API"""
        # Create player and give credits
        game_api.create_player("TestPlayer")
        
        # This should fail due to insufficient credits
        result = game_api.upgrade_hardware("TestPlayer", "cpu")
        
        assert result["success"] == False
        assert "credits" in result["error"].lower()
    
    def test_get_leaderboard_api(self, game_api):
        """Test leaderboard through API"""
        # Create some players
        game_api.create_player("Player1")
        game_api.create_player("Player2")
        
        result = game_api.get_leaderboard("level", 10)
        
        assert result["success"] == True
        assert isinstance(result["data"], list)
        assert len(result["data"]) >= 2
    
    def test_get_server_statistics(self, game_api):
        """Test server statistics"""
        result = game_api.get_server_statistics()
        
        assert result["success"] == True
        assert "total_players" in result["data"]
        assert "online_players" in result["data"]
        assert "total_missions" in result["data"]
    
    def test_passive_mining_api(self, game_api):
        """Test passive mining through API"""
        # Create player
        game_api.create_player("TestPlayer")
        
        # Start mining
        result = game_api.start_passive_mining("TestPlayer", 1)
        
        assert result["success"] == True
        assert "started" in result["message"].lower()
        
        # Check mining status
        result = game_api.check_passive_mining("TestPlayer")
        
        assert result["success"] == True
        assert "progress" in result["message"].lower()
    
    def test_validate_player_session(self, game_api):
        """Test session validation"""
        # Create and authenticate player
        game_api.create_player("TestPlayer")
        game_api.authenticate_player("TestPlayer", "session123")
        
        # Validate session
        valid = game_api.validate_player_session("TestPlayer", "session123")
        assert valid == True
        
        # Invalid session
        valid = game_api.validate_player_session("TestPlayer", "wrong_session")
        assert valid == False
        
        # Nonexistent player
        valid = game_api.validate_player_session("NonExistent", "session123")
        assert valid == False