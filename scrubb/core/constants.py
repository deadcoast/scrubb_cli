"""Constants for scrubb application.

This module defines all named constants used throughout the application,
eliminating magic numbers and strings.
"""

from enum import Enum


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INVALID_INPUT = 2
EXIT_USER_CANCELLED = 130

# File size units (in bytes)
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

# Default limits
MAX_FILES_PER_DIR_DISPLAY = 100
MAX_TREE_DEPTH_DISPLAY = 10
MAX_ERRORS_TO_DISPLAY = 10

# Configuration keys
CONFIG_KEY_DEFAULT_ROOT = "default_root"
CONFIG_KEY_IGNORE_PATTERNS = "ignore_patterns"
CONFIG_KEY_TEXT_EXTENSIONS = "text_extensions"
CONFIG_KEY_CLASSIFICATION_RULES = "classification_rules"
CONFIG_KEY_SCRUBBED_FOLDER_NAME = "scrubbed_folder_name"


class OperationStatus(Enum):
    """Status of an operation.
    
    Used to track the current state of long-running operations.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorSeverity(Enum):
    """Severity level of an error.
    
    Used to classify errors by their impact on functionality.
    """
    CRITICAL = "critical"  # Prevents primary function
    WARNING = "warning"    # Doesn't prevent primary function
    INFO = "info"          # Informational only
