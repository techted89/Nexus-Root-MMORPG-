import unittest
from src.mission import Mission, MissionManager
from src.player import Player

class TestMission(unittest.TestCase):
    def test_mission_creation(self):
        mission = Mission("First Hack", "Hack into the megacorp server.", 100)
        self.assertEqual(mission.name, "First Hack")
        self.assertEqual(mission.description, "Hack into the megacorp server.")
        self.assertEqual(mission.reward, 100)
        self.assertFalse(mission.is_completed)

    def test_mission_completion(self):
        player = Player("Jules")
        mission = Mission("First Hack", "Hack into the megacorp server.", 100)
        mission.complete(player)
        self.assertTrue(mission.is_completed)
        self.assertEqual(player.vc_state.level, 2)

    def test_mission_manager(self):
        mission_manager = MissionManager()
        mission = Mission("First Hack", "Hack into the megacorp server.", 100)
        mission_manager.add_mission(mission)
        self.assertEqual(len(mission_manager.missions), 1)
        retrieved_mission = mission_manager.get_mission("First Hack")
        self.assertEqual(retrieved_mission, mission)

if __name__ == '__main__':
    unittest.main()
