class BaseObject:
    """
    Base class for all NexusScript objects.
    """
    def __init__(self, object_type):
        self.object_type = object_type

    def __str__(self):
        return f"BaseObject(type='{self.object_type}')"
