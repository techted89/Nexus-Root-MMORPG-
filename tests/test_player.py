import unittest
import sys
sys.path.append('src')
from player import Player

class TestPlayer(unittest.TestCase):
    def test_player_creation(self):
        player = Player("Jules")
        self.assertEqual(player.name, "Jules")
        self.assertEqual(player.level, 1)
        self.assertEqual(player.experience, 0)
        self.assertEqual(player.skills, {})

    def test_add_experience(self):
        player = Player("Jules")
        player.add_experience(100)
        self.assertEqual(player.experience, 100)

    def test_learn_skill(self):
        player = Player("Jules")
        player.learn_skill("hacking", 1)
        self.assertEqual(player.skills, {"hacking": 1})

if __name__ == '__main__':
    unittest.main()
