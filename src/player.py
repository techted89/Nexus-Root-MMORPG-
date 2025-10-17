from .vc_state import VC_State

class Player:
    def __init__(self, name, is_vip=False):
        self.name = name
        self.vc_state = VC_State()
        self.is_vip = is_vip

    def update_xp(self, amount):
        self.vc_state.experience += amount
        if self.vc_state.experience >= self.vc_state.level * 100:
            self.vc_state.level += 1
            print(f"Level up! You are now level {self.vc_state.level}.")

    def check_kmap(self, command):
        return self.vc_state.check_kmap(command)
