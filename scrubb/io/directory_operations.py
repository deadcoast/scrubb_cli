"""Real implementation of directory operations.

This module provides the concrete implementation of DirectoryOperations
that interacts with the actual file system.
"""

from pathlib import Path
from typing import List
from ..core.result import Result, Success, Failure
from ..core.errors import DirectoryOperationError


class RealDirectoryOperations:
    """Real implementation of directory operations.
    
    This class provides directory operations that interact with the actual
    file system. All operations return Result types for explicit error handling.
    """
    
    def create_directory(self, path: Path) -> Result[None]:
        """Create directory.
        
        Creates the directory and any necessary parent directories.
        If the directory already exists, this is considered a success.
        
        Args:
            path: Path to directory to create
            
        Returns:
            Result[None]: Success or error with context
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return Success(None)
        except PermissionError as e:
            return Failure(DirectoryOperationError(
                "Permission denied creating directory",
                context={"path": str(path), "error": str(e)}
            ))
        except OSError as e:
            return Failure(DirectoryOperationError(
                "Failed to create directory",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(DirectoryOperationError(
                "Unexpected error creating directory",
                context={"path": str(path), "error": str(e)}
            ))
    
    def remove_directory(self, path: Path) -> Result[None]:
        """Remove empty directory.
        
        Only removes the directory if it is empty. If the directory
        is not empty, this will fail.
        
        Args:
            path: Path to directory to remove
            
        Returns:
            Result[None]: Success or error with context
        """
        try:
            path.rmdir()
            return Success(None)
        except FileNotFoundError as e:
            return Failure(DirectoryOperationError(
                "Directory not found",
                context={"path": str(path), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(DirectoryOperationError(
                "Permission denied removing directory",
                context={"path": str(path), "error": str(e)}
            ))
        except OSError as e:
            # OSError includes cases where directory is not empty
            return Failure(DirectoryOperationError(
                "Failed to remove directory (may not be empty)",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(DirectoryOperationError(
                "Unexpected error removing directory",
                context={"path": str(path), "error": str(e)}
            ))
    
    def list_directory(self, path: Path) -> Result[List[Path]]:
        """List directory contents.
        
        Returns a list of all items (files and directories) in the directory.
        
        Args:
            path: Path to directory to list
            
        Returns:
            Result[List[Path]]: List of paths on success, error on failure
        """
        try:
            items = list(path.iterdir())
            return Success(items)
        except FileNotFoundError as e:
            return Failure(DirectoryOperationError(
                "Directory not found",
                context={"path": str(path), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(DirectoryOperationError(
                "Permission denied listing directory",
                context={"path": str(path), "error": str(e)}
            ))
        except OSError as e:
            return Failure(DirectoryOperationError(
                "Failed to list directory",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(DirectoryOperationError(
                "Unexpected error listing directory",
                context={"path": str(path), "error": str(e)}
            ))
    
    def is_empty(self, path: Path) -> Result[bool]:
        """Check if directory is empty.
        
        This is an O(1) operation - it just checks if any entry exists
        without iterating through all entries.
        
        Args:
            path: Path to directory to check
            
        Returns:
            Result[bool]: True if empty on success, error on failure
        """
        try:
            # O(1) check - just try to get the first item
            first_item = next(path.iterdir(), None)
            # If first_item is None, directory is empty
            return Success(first_item is None)
        except FileNotFoundError as e:
            return Failure(DirectoryOperationError(
                "Directory not found",
                context={"path": str(path), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(DirectoryOperationError(
                "Permission denied checking directory",
                context={"path": str(path), "error": str(e)}
            ))
        except OSError as e:
            return Failure(DirectoryOperationError(
                "Failed to check directory",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(DirectoryOperationError(
                "Unexpected error checking directory",
                context={"path": str(path), "error": str(e)}
            ))
    
    def directory_exists(self, path: Path) -> bool:
        """Check if directory exists.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if directory exists, False otherwise
        """
        return path.exists() and path.is_dir()
