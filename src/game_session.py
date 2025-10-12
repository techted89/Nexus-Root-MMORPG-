class GameSession:
    def __init__(self, players):
        self.players = players
        self.difficulty_score = self.calculate_difficulty_score()

    def calculate_difficulty_score(self):
        if not self.players:
            return 0
        total_c_xp = sum(player.vc_state.c_xp for player in self.players)
        return (total_c_xp / len(self.players)) / 100
