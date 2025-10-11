class VC_State:
    def __init__(self):
        self.level = 1
        self.experience = 0
        self.credits = 0
        self.ram_max = 1
        self.cpu_max = 1
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
