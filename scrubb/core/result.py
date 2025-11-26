"""Result types for explicit error handling.

This module provides Result types that make success/failure explicit,
eliminating the need for exception handling in business logic.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')


@dataclass(frozen=True)
class Success(Generic[T]):
    """Successful operation result.
    
    Attributes:
        value: The successful result value
    """
    value: T
    
    def is_success(self) -> bool:
        """Check if result is success.
        
        Returns:
            bool: Always True for Success
        """
        return True
    
    def is_failure(self) -> bool:
        """Check if result is failure.
        
        Returns:
            bool: Always False for Success
        """
        return False
    
    def unwrap(self) -> T:
        """Unwrap the success value.
        
        Returns:
            T: The success value
        """
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Unwrap the success value or return default.
        
        Args:
            default: Default value (unused for Success)
            
        Returns:
            T: The success value
        """
        return self.value


@dataclass(frozen=True)
class Failure(Generic[T]):
    """Failed operation result.
    
    Attributes:
        error: The error that caused the failure
    """
    error: Exception
    
    def is_success(self) -> bool:
        """Check if result is success.
        
        Returns:
            bool: Always False for Failure
        """
        return False
    
    def is_failure(self) -> bool:
        """Check if result is failure.
        
        Returns:
            bool: Always True for Failure
        """
        return True
    
    def unwrap(self) -> T:
        """Unwrap the value (raises the error).
        
        Returns:
            T: Never returns
            
        Raises:
            Exception: The error that caused the failure
        """
        raise self.error
    
    def unwrap_or(self, default: T) -> T:
        """Unwrap the value or return default.
        
        Args:
            default: Default value to return on failure
            
        Returns:
            T: The default value
        """
        return default


# Type alias for Result
Result = Union[Success[T], Failure[T]]


@dataclass
class OperationResult:
    """Result of a file organization operation.
    
    Attributes:
        files_moved: Number of files successfully moved
        files_by_category: Count of files by category
        empty_folders_removed: Number of empty folders removed
        critical_errors: List of critical errors that occurred
        warnings: List of warnings that occurred
    """
    files_moved: int
    files_by_category: dict[str, int]
    empty_folders_removed: int
    critical_errors: list[Exception]
    warnings: list[Exception]
    
    @property
    def success(self) -> bool:
        """Operation succeeded if no critical errors.
        
        Returns:
            bool: True if no critical errors, False otherwise
        """
        return len(self.critical_errors) == 0
    
    @property
    def total_errors(self) -> int:
        """Total number of errors (critical + warnings).
        
        Returns:
            int: Total error count
        """
        return len(self.critical_errors) + len(self.warnings)
