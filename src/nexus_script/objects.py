import random

class IP_Object:
    def __init__(self, octets):
        if len(octets) != 4:
            raise ValueError("IP address must have 4 octets")
        self.octets = octets

    def __str__(self):
        return ".".join(map(str, self.octets))

    def ping(self):
        return random.choice([True, False])

class Port_Object:
    def __init__(self, port_number, service):
        self.port_number = port_number
        self.service = service

class Exploit_Object:
    def __init__(self, name, target_service):
        self.name = name
        self.target_service = target_service

    def inject(self, target):
        # TODO: Implement exploit injection logic
        pass
