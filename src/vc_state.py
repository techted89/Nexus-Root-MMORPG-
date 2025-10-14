class VC_State:
    def __init__(self):
        self.level = 1
        self.experience = 0
        self.c_xp = 0
        self.credits = 0
        self.ram_max = 1
        self.cpu_max = 1
        self.theme = "default"
        self.prompt_format = "{user}@nexus-root> "
        self.skins = []
        self.passive_mining_end_time = None
        self.cpu_tier = 1
        self.ram_tier = 1
        self.nic_tier = 1
        self.ssd_tier = 1
        self.kmap_state = {
            "set": "INTEGRATED",
            "scan": "LOCKED",
            "run": "LOCKED",
            "hashcrack": "LOCKED",
            "pivot": "LOCKED",
            "thread spawn": "LOCKED",
            "raw": "LOCKED",
            "ls": "INTEGRATED",
            "cat": "INTEGRATED",
            "print": "INTEGRATED",
            "edit": "LOCKED"
        }

    def check_kmap(self, command):
        return self.kmap_state.get(command, "LOCKED")

    def get_max_threads(self):
        from src.upgrade_data import UPGRADE_DATA
        return UPGRADE_DATA['ram'][self.ram_tier]['max_threads']
