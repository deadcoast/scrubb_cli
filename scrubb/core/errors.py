"""Exception hierarchy for scrubb.

This module defines all custom exceptions used throughout the application.
All exceptions include a context dictionary for debugging.
"""

from typing import Any


class ScrubbError(Exception):
    """Base exception for all scrubb errors.
    
    All scrubb exceptions inherit from this base class and include
    a context dictionary for additional debugging information.
    
    Attributes:
        message: Human-readable error message
        context: Dictionary of contextual information about the error
    """
    
    def __init__(self, message: str, context: dict[str, Any] | None = None):
        """Initialize ScrubbError.
        
        Args:
            message: Human-readable error message
            context: Optional dictionary of contextual information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self) -> str:
        """String representation of the error.
        
        Returns:
            str: Error message with context if available
        """
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class ValidationError(ScrubbError):
    """Input validation failed.
    
    Raised when user input or function parameters fail validation checks.
    """
    pass


class ConfigurationError(ScrubbError):
    """Configuration is invalid.
    
    Raised when configuration file or settings are invalid or incomplete.
    """
    pass


class FileOperationError(ScrubbError):
    """File operation failed.
    
    Raised when file I/O operations (read, write, move, delete) fail.
    """
    pass


class DirectoryOperationError(ScrubbError):
    """Directory operation failed.
    
    Raised when directory operations (create, remove, list) fail.
    """
    pass


class PathSecurityError(ScrubbError):
    """Path validation failed for security reasons.
    
    Raised when path validation detects potential security issues like
    directory traversal attempts or paths outside allowed boundaries.
    """
    pass


class ClassificationError(ScrubbError):
    """File classification failed.
    
    Raised when file classification encounters an error.
    """
    pass
