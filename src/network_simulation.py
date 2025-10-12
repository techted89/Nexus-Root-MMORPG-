class Service:
    def __init__(self, name, version, port, is_vulnerable=False):
        self.name = name
        self.version = version
        self.port = port
        self.is_vulnerable = is_vulnerable

class Firewall:
    def __init__(self, rules=None):
        self.rules = rules if rules is not None else []

    def check(self, source_ip, dest_port):
        # Simplified check
        for rule in self.rules:
            if rule['port'] == dest_port and rule['action'] == 'DROP':
                return False
        return True

class IDS_Object:
    def __init__(self, rules=None):
        self.rules = rules if rules is not None else []

class TargetDevice:
    def __init__(self, ip_address, os):
        self.ip_address = ip_address
        self.os = os
        self.services = []
        self.firewall = Firewall()
        self.ids = IDS_Object()
        self.filesystem = {}

    def add_service(self, service):
        self.services.append(service)

class Network:
    def __init__(self, topology_template):
        self.topology_template = topology_template
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)
