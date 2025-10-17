"""
Tests for player service
"""

import pytest
import tempfile
import os
from src.services.player_service import PlayerService
from src.repositories.sqlite_player_repository import SQLitePlayerRepository
from src.core.events import EventBus
from src.core.exceptions import ValidationError, InsufficientCreditsError

class TestPlayerService:
    """Test cases for PlayerService"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def player_service(self, temp_db):
        """Create player service with temporary database"""
        repository = SQLitePlayerRepository(temp_db)
        event_bus = EventBus()
        return PlayerService(repository, event_bus)
    
    def test_create_player_success(self, player_service):
        """Test successful player creation"""
        player = player_service.create_player("TestPlayer", is_vip=False)
        
        assert player.name == "TestPlayer"
        assert player.is_vip == False
        assert player.stats.level == 1
        assert player.stats.credits == 0
        assert player.id is not None
    
    def test_create_player_invalid_name(self, player_service):
        """Test player creation with invalid name"""
        with pytest.raises(ValidationError):
            player_service.create_player("a")  # Too short
        
        with pytest.raises(ValidationError):
            player_service.create_player("a" * 25)  # Too long
        
        with pytest.raises(ValidationError):
            player_service.create_player("test@player")  # Invalid characters
    
    def test_create_duplicate_player(self, player_service):
        """Test creating duplicate player"""
        player_service.create_player("TestPlayer")
        
        with pytest.raises(ValidationError):
            player_service.create_player("TestPlayer")
    
    def test_authenticate_player(self, player_service):
        """Test player authentication"""
        # Create player
        created_player = player_service.create_player("TestPlayer")
        
        # Authenticate
        auth_player = player_service.authenticate_player("TestPlayer", "session123")
        
        assert auth_player is not None
        assert auth_player.name == "TestPlayer"
        assert auth_player.session_id == "session123"
        assert auth_player.is_online == True
    
    def test_update_experience(self, player_service):
        """Test experience update and level up"""
        player = player_service.create_player("TestPlayer")
        
        # Update experience (not enough to level up)
        leveled_up = player_service.update_experience(player, 50)
        assert leveled_up == False
        assert player.stats.level == 1
        assert player.stats.experience == 50
        
        # Update experience (enough to level up)
        leveled_up = player_service.update_experience(player, 60)
        assert leveled_up == True
        assert player.stats.level == 2
        assert player.stats.experience == 10  # 110 - 100
    
    def test_update_credits(self, player_service):
        """Test credits update"""
        player = player_service.create_player("TestPlayer")
        
        # Add credits
        success = player_service.update_credits(player, 100, "test reward")
        assert success == True
        assert player.stats.credits == 100
        
        # Spend credits
        success = player_service.update_credits(player, -50, "test purchase")
        assert success == True
        assert player.stats.credits == 50
        
        # Try to spend more than available
        with pytest.raises(InsufficientCreditsError):
            player_service.update_credits(player, -100, "insufficient")
    
    def test_upgrade_hardware(self, player_service):
        """Test hardware upgrade"""
        player = player_service.create_player("TestPlayer")
        
        # Give player some credits
        player_service.update_credits(player, 1000, "test")
        
        # Upgrade CPU
        success, message = player_service.upgrade_hardware(player, "cpu")
        assert success == True
        assert player.virtual_computer.cpu.tier == 2
        assert player.stats.credits < 1000  # Credits should be deducted
    
    def test_upgrade_hardware_insufficient_credits(self, player_service):
        """Test hardware upgrade with insufficient credits"""
        player = player_service.create_player("TestPlayer")
        
        # Try to upgrade without enough credits
        with pytest.raises(InsufficientCreditsError):
            player_service.upgrade_hardware(player, "cpu")
    
    def test_unlock_command(self, player_service):
        """Test command unlocking"""
        player = player_service.create_player("TestPlayer")
        
        # Initially scan should be locked
        assert "scan" not in player.knowledge_map.integrated_commands
        assert "scan" not in player.knowledge_map.unlocked_commands
        
        # Unlock scan command
        success = player_service.unlock_command(player, "scan")
        assert success == True
        assert "scan" in player.knowledge_map.unlocked_commands
    
    def test_passive_mining(self, player_service):
        """Test passive mining"""
        player = player_service.create_player("TestPlayer")
        
        # Start mining
        success = player_service.start_passive_mining(player, 1)
        assert success == True
        assert player.virtual_computer.passive_mining_end_time is not None
        
        # Try to start again (should fail)
        success = player_service.start_passive_mining(player, 1)
        assert success == False
    
    def test_get_leaderboard(self, player_service):
        """Test leaderboard functionality"""
        # Create multiple players
        player1 = player_service.create_player("Player1")
        player2 = player_service.create_player("Player2")
        player3 = player_service.create_player("Player3")
        
        # Give different levels
        player_service.update_experience(player1, 150)  # Level 2
        player_service.update_experience(player2, 300)  # Level 3
        # Player3 stays at level 1
        
        # Get leaderboard
        leaderboard = player_service.get_leaderboard(limit=5, category="level")
        
        assert len(leaderboard) == 3
        assert leaderboard[0]["name"] == "Player2"  # Highest level
        assert leaderboard[0]["level"] == 3
        assert leaderboard[1]["name"] == "Player1"
        assert leaderboard[1]["level"] == 2