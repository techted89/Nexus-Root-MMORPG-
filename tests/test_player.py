import unittest
from src.player import Player

class TestPlayer(unittest.TestCase):
    def test_player_creation(self):
        player = Player("Jules")
        self.assertEqual(player.name, "Jules")
        self.assertEqual(player.vc_state.level, 1)

    def test_update_xp(self):
        player = Player("Jules")
        player.update_xp(100)
        self.assertEqual(player.vc_state.level, 2)

if __name__ == '__main__':
    unittest.main()
