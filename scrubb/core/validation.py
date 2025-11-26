"""Input validation functions.

This module provides validation functions for inputs at system boundaries.
All validation functions raise ValidationError on invalid input.
"""

from pathlib import Path
from typing import Any
import re

from .errors import ValidationError


def validate_path_string(path_str: str) -> str:
    """Validate a path string.
    
    Args:
        path_str: Path string to validate
        
    Returns:
        str: The validated path string
        
    Raises:
        ValidationError: If path string is invalid
    """
    if not path_str:
        raise ValidationError(
            "Path cannot be empty",
            context={"path": path_str}
        )
    
    if not isinstance(path_str, str):
        raise ValidationError(
            "Path must be a string",
            context={"path": path_str, "type": type(path_str).__name__}
        )
    
    # Check for null bytes
    if '\0' in path_str:
        raise ValidationError(
            "Path contains null bytes",
            context={"path": path_str}
        )
    
    return path_str


def validate_path_exists(path: Path) -> Path:
    """Validate that a path exists.
    
    Args:
        path: Path to validate
        
    Returns:
        Path: The validated path
        
    Raises:
        ValidationError: If path does not exist
    """
    if not path.exists():
        raise ValidationError(
            "Path does not exist",
            context={"path": str(path)}
        )
    
    return path


def validate_directory_path(path: Path) -> Path:
    """Validate that a path is a directory.
    
    Args:
        path: Path to validate
        
    Returns:
        Path: The validated directory path
        
    Raises:
        ValidationError: If path is not a directory
    """
    if not path.is_dir():
        raise ValidationError(
            "Path is not a directory",
            context={"path": str(path)}
        )
    
    return path


def validate_file_path(path: Path) -> Path:
    """Validate that a path is a file.
    
    Args:
        path: Path to validate
        
    Returns:
        Path: The validated file path
        
    Raises:
        ValidationError: If path is not a file
    """
    if not path.is_file():
        raise ValidationError(
            "Path is not a file",
            context={"path": str(path)}
        )
    
    return path


def validate_regex_pattern(pattern: str) -> str:
    """Validate that a string is a valid regex pattern.
    
    Args:
        pattern: Regex pattern to validate
        
    Returns:
        str: The validated pattern
        
    Raises:
        ValidationError: If pattern is not valid regex
    """
    try:
        re.compile(pattern)
        return pattern
    except re.error as e:
        raise ValidationError(
            "Invalid regex pattern",
            context={"pattern": pattern, "error": str(e)}
        )


def validate_positive_integer(value: Any, name: str = "value") -> int:
    """Validate that a value is a positive integer.
    
    Args:
        value: Value to validate
        name: Name of the value for error messages
        
    Returns:
        int: The validated integer
        
    Raises:
        ValidationError: If value is not a positive integer
    """
    if not isinstance(value, int):
        raise ValidationError(
            f"{name} must be an integer",
            context={name: value, "type": type(value).__name__}
        )
    
    if value <= 0:
        raise ValidationError(
            f"{name} must be positive",
            context={name: value}
        )
    
    return value


def validate_non_negative_integer(value: Any, name: str = "value") -> int:
    """Validate that a value is a non-negative integer.
    
    Args:
        value: Value to validate
        name: Name of the value for error messages
        
    Returns:
        int: The validated integer
        
    Raises:
        ValidationError: If value is not a non-negative integer
    """
    if not isinstance(value, int):
        raise ValidationError(
            f"{name} must be an integer",
            context={name: value, "type": type(value).__name__}
        )
    
    if value < 0:
        raise ValidationError(
            f"{name} must be non-negative",
            context={name: value}
        )
    
    return value


def validate_string_not_empty(value: Any, name: str = "value") -> str:
    """Validate that a value is a non-empty string.
    
    Args:
        value: Value to validate
        name: Name of the value for error messages
        
    Returns:
        str: The validated string
        
    Raises:
        ValidationError: If value is not a non-empty string
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"{name} must be a string",
            context={name: value, "type": type(value).__name__}
        )
    
    if not value.strip():
        raise ValidationError(
            f"{name} cannot be empty",
            context={name: value}
        )
    
    return value


def validate_configuration_dict(config: Any) -> dict:
    """Validate that configuration is a dictionary.
    
    Args:
        config: Configuration to validate
        
    Returns:
        dict: The validated configuration dictionary
        
    Raises:
        ValidationError: If config is not a dictionary
    """
    if not isinstance(config, dict):
        raise ValidationError(
            "Configuration must be a dictionary",
            context={"type": type(config).__name__}
        )
    
    return config
