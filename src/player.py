from .vc_state import VC_State

class Player:
    def __init__(self, name, is_vip=False):
        self.name = name
        self.vc_state = VC_State()
        self.is_vip = is_vip

    def update_xp(self, amount):
        self.vc_state.experience += amount
        # Level up every 100 experience points
        if self.vc_state.experience >= self.vc_state.level * 100:
            self.vc_state.level += 1
            print(f"Level up! You are now level {self.vc_state.level}.")

    def check_kmap(self, command):
        return self.vc_state.check_kmap(command)

    def scan_file_for_fragment(self, content):
        if "CMD_DECLARE: PIVOT" in content:
            self.vc_state.kmap_state["pivot"] = "DISCOVERED"
            return "Knowledge fragment for 'pivot' discovered!"
        return None

if __name__ == '__main__':
    player = Player("Jules")
    print(f"Player {player.name} created.")
    player.update_xp(1)
    print(f"{player.name}'s level: {player.vc_state.level}")
    print(f"{player.name}'s kmap for 'scan': {player.check_kmap('scan')}")
