"""Verbosity management for CLI output control."""

from enum import Enum
from contextvars import ContextVar
from typing import Optional


class VerbosityLevel(Enum):
    """Verbosity levels for output control."""
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


# Global context variable for verbosity state
_verbosity_context: ContextVar[Optional['VerbosityManager']] = ContextVar(
    'verbosity_context', 
    default=None
)


class VerbosityManager:
    """Manages output verbosity levels."""
    
    def __init__(self, level: VerbosityLevel = VerbosityLevel.NORMAL):
        """Initialize verbosity manager with specified level.
        
        Args:
            level: The verbosity level to use (default: NORMAL)
        """
        self.level = level
    
    def should_print_debug(self) -> bool:
        """Check if debug messages should be printed.
        
        Returns:
            True if verbosity level is VERBOSE, False otherwise
        """
        return self.level == VerbosityLevel.VERBOSE
    
    def should_print_info(self) -> bool:
        """Check if info messages should be printed.
        
        Returns:
            True if verbosity level is NORMAL or VERBOSE, False if QUIET
        """
        return self.level in (VerbosityLevel.NORMAL, VerbosityLevel.VERBOSE)
    
    def should_print_summary(self) -> bool:
        """Check if summary should be printed.
        
        Returns:
            True if verbosity level is NORMAL or VERBOSE, False if QUIET
        """
        return self.level in (VerbosityLevel.NORMAL, VerbosityLevel.VERBOSE)
    
    def should_print_error(self) -> bool:
        """Check if error messages should be printed.
        
        Returns:
            Always True - errors are printed at all verbosity levels
        """
        return True
    
    def should_print_warning(self) -> bool:
        """Check if warning messages should be printed.
        
        Returns:
            Always True - warnings are printed at all verbosity levels
        """
        return True
    
    @classmethod
    def get_current(cls) -> 'VerbosityManager':
        """Get the current verbosity manager from context.
        
        Returns:
            The current VerbosityManager, or a new one with NORMAL level if none set
        """
        manager = _verbosity_context.get()
        if manager is None:
            manager = cls(VerbosityLevel.NORMAL)
        return manager
    
    @classmethod
    def set_current(cls, manager: 'VerbosityManager') -> None:
        """Set the current verbosity manager in context.
        
        Args:
            manager: The VerbosityManager to set as current
        """
        _verbosity_context.set(manager)
    
    def __repr__(self) -> str:
        """String representation of VerbosityManager."""
        return f"VerbosityManager(level={self.level.name})"
