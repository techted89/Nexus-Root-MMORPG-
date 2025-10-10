class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.experience = 0
        self.skills = {}

    def add_experience(self, amount):
        self.experience += amount
        # TODO: Add level up logic

    def learn_skill(self, skill_name, skill_level):
        self.skills[skill_name] = skill_level

if __name__ == '__main__':
    player = Player("Jules")
    print(f"Player {player.name} created.")
    player.add_experience(100)
    print(f"{player.name}'s experience: {player.experience}")
    player.learn_skill("hacking", 1)
    print(f"{player.name}'s skills: {player.skills}")
