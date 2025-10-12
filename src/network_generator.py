import random
import math
from .network_simulation import Network, TargetDevice, Service

class NetworkGenerator:
    def __init__(self, game_session):
        self.game_session = game_session
        self.difficulty_score = game_session.difficulty_score

    def generate_network(self):
        topology_template = random.choice(['Linear', 'Hub-and-Spoke'])
        network = Network(topology_template)

        subnet = f"10.1.{random.randint(1, 254)}.0/24"
        num_layers = math.ceil(self.difficulty_score / 25) if self.difficulty_score > 0 else 1

        for i in range(num_layers):
            ip = f"10.1.{subnet.split('.')[2]}.{random.randint(1, 254)}"
            os = random.choice(['Windows', 'Linux'])
            device = TargetDevice(ip, os)

            self._configure_device_security(device, i + 1)
            network.add_device(device)

        return network

    def _configure_device_security(self, device, layer_num):
        d_score = self.difficulty_score

        service_pools = {
            'low': [Service("FTP", "vsftpd 2.3.4", 21, is_vulnerable=True), Service("Telnet", "GNU inetutils 1.9.4", 23, is_vulnerable=True)],
            'medium': [Service("SSH", "OpenSSH 7.2", 22), Service("SMTP", "Postfix 3.1.0", 25)],
            'high': [Service("HTTP", "Apache 2.4.29", 80), Service("HTTPS", "Nginx 1.14.0", 443)]
        }

        if d_score <= 25:
            service = random.choice(service_pools['low'])
        elif d_score <= 50:
            service = random.choice(service_pools['medium'])
        else:
            service = random.choice(service_pools['high'])

        device.add_service(service)

        if d_score > 50:
            device.firewall.rules.append({'port': random.choice([21, 23]), 'action': 'DROP'})

        if d_score > 75:
            device.ids.rules.append("LOG_ALL_CONNECTIONS")

    def generate_pvp_lan_zone(self, players):
        network = Network('PvP_LAN_Zone')
        subnet = f"192.168.{random.randint(1, 254)}.0/24"

        for player in players:
            ip = f"192.168.{subnet.split('.')[2]}.{random.randint(1, 254)}"
            device = TargetDevice(ip, "Custom")
            # Add a basic firewall rule for defense
            device.firewall.rules.append({'port': 22, 'action': 'ALLOW'})
            network.add_device(device)

        # Objective file placement based on complexity
        objective_files = {"FileA.txt": "simple", "FileB.txt": "medium", "FileC.txt": "hard"}

        devices = network.devices
        random.shuffle(devices)

        for i, (file, complexity) in enumerate(objective_files.items()):
            target_device = devices[i % len(devices)]
            if complexity == "simple":
                target_device.add_service(Service("FTP", "vsftpd 3.0.3", 21, is_vulnerable=True))
            elif complexity == "medium":
                target_device.add_service(Service("SSH", "OpenSSH 8.2", 22))
            else: # hard
                target_device.add_service(Service("HTTPS", "Nginx 1.18.0", 443))

            target_device.filesystem[file] = f"Critical data ({complexity}): {random.random()}"

        return network
