UPGRADE_DATA = {
    "cpu": {
        1: {"cost": 0, "effect": 1.0},
        2: {"cost": 100, "effect": 0.9},
        3: {"cost": 250, "effect": 0.8},
        4: {"cost": 500, "effect": 0.7},
        5: {"cost": 1000, "effect": 0.6},
        6: {"cost": 2000, "effect": 0.5},
        7: {"cost": 4000, "effect": 0.4},
        8: {"cost": 8000, "effect": 0.3},
        9: {"cost": 16000, "effect": 0.2},
        10: {"cost": 32000, "effect": 0.1},
    },
    "ram": {
        1: {"cost": 0, "max_threads": 1},
        2: {"cost": 100, "max_threads": 1},
        3: {"cost": 250, "max_threads": 2},
        4: {"cost": 500, "max_threads": 2},
        5: {"cost": 1000, "max_threads": 3},
        6: {"cost": 2000, "max_threads": 3},
        7: {"cost": 4000, "max_threads": 4},
        8: {"cost": 8000, "max_threads": 4},
        9: {"cost": 16000, "max_threads": 5},
        10: {"cost": 32000, "max_threads": 5},
    },
    "nic": {
        # Placeholder for future implementation
        1: {"cost": 0, "speed": 10},
        2: {"cost": 100, "speed": 25},
    },
    "ssd": {
        # Placeholder for future implementation
        1: {"cost": 0, "size": 100},
        2: {"cost": 100, "size": 250},
    }
}
