from .base_object import BaseObject

class IPObject(BaseObject):
    """
    Represents an IP address in the game.
    """
    def __init__(self, address):
        super().__init__("IP_Object")
        self.address = address

    def ping(self):
        """
        Simulates pinging the IP address.
        """
        import random
        return random.choice([True, False])

    def __str__(self):
        return f"IPObject(address='{self.address}')"
