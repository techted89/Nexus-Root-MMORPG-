"""
Custom exceptions for Nexus Root MMORPG
"""

class NexusException(Exception):
    """Base exception for all Nexus Root errors"""
    def __init__(self, message: str, code: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.context = context or {}

class ValidationError(NexusException):
    """Raised when input validation fails"""
    pass

class AuthenticationError(NexusException):
    """Raised when authentication fails"""
    pass

class CommandNotFoundError(NexusException):
    """Raised when a command is not found or locked"""
    pass

class InsufficientCreditsError(NexusException):
    """Raised when player doesn't have enough credits"""
    pass

class InsufficientResourcesError(NexusException):
    """Raised when system resources are insufficient"""
    pass

class ScriptExecutionError(NexusException):
    """Raised when NexusScript execution fails"""
    pass

class DatabaseError(NexusException):
    """Raised when database operations fail"""
    pass

class ConfigurationError(NexusException):
    """Raised when configuration is invalid"""
    pass