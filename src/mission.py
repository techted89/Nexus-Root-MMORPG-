class Mission:
    def __init__(self, name, description, reward):
        self.name = name
        self.description = description
        self.reward = reward
        self.is_completed = False

    def complete(self, player):
        self.is_completed = True
        player.update_xp(self.reward)
        print(f"Mission '{self.name}' completed! You gained {self.reward} experience.")

class MissionManager:
    def __init__(self):
        self.missions = []

    def add_mission(self, mission):
        self.missions.append(mission)

    def get_mission(self, mission_name):
        for mission in self.missions:
            if mission.name == mission_name:
                return mission
        return None
