import random

class IP_Object:
    def __init__(self, octet1, octet2, octet3, octet4):
        self.address = f"{octet1}.{octet2}.{octet3}.{octet4}"

    def ping(self):
        return random.choice([True, False])

    def __str__(self):
        return f"IP_Object({self.address})"

class Port_Object:
    def __init__(self, port_number, service_name, version=""):
        self.port_number = port_number
        self.service_name = service_name
        self.version = version
        self.is_open = True

    def __str__(self):
        return f"Port({self.port_number}, {self.service_name}, v{self.version})"

class Exploit_Object:
    def __init__(self, name, target_service, target_version):
        self.name = name
        self.target_service = target_service
        self.target_version = target_version

    def deploy(self, target_ip, target_os, payload_module):
        # In a real implementation, this would contain complex logic
        # to determine if the exploit is successful.
        return "Exploit deployed. Target compromised."

    def __str__(self):
        return f"Exploit({self.name})"
