"""File operations implementation.

This module provides concrete implementation of file I/O operations
that return Result types for explicit error handling.
"""

import shutil
from pathlib import Path
from typing import Union

from ..core.result import Result, Success, Failure
from ..core.errors import FileOperationError


class RealFileOperations:
    """Real file system operations implementation.
    
    This class implements the FileOperations protocol, providing
    actual file system operations that return Result types.
    All exceptions are caught and converted to Failure results.
    """
    
    def read_file(self, path: Path) -> Result[str]:
        """Read file content.
        
        Args:
            path: Path to file to read
            
        Returns:
            Result[str]: File content on success, error on failure
        """
        try:
            content = path.read_text(encoding='utf-8')
            return Success(content)
        except FileNotFoundError as e:
            return Failure(FileOperationError(
                f"File not found: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(FileOperationError(
                f"Permission denied reading file: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except UnicodeDecodeError as e:
            return Failure(FileOperationError(
                f"Failed to decode file as UTF-8: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(FileOperationError(
                f"Failed to read file: {path}",
                context={"path": str(path), "error": str(e), "error_type": type(e).__name__}
            ))
    
    def write_file(self, path: Path, content: str) -> Result[None]:
        """Write content to file.
        
        Args:
            path: Path to file to write
            content: Content to write
            
        Returns:
            Result[None]: Success or error
        """
        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            return Success(None)
        except PermissionError as e:
            return Failure(FileOperationError(
                f"Permission denied writing file: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except OSError as e:
            return Failure(FileOperationError(
                f"Failed to write file: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(FileOperationError(
                f"Failed to write file: {path}",
                context={"path": str(path), "error": str(e), "error_type": type(e).__name__}
            ))

    def move_file(self, source: Path, destination: Path) -> Result[None]:
        """Move file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Result[None]: Success or error
        """
        try:
            # Ensure destination parent directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Use shutil.move for cross-platform compatibility
            shutil.move(str(source), str(destination))
            return Success(None)
        except FileNotFoundError as e:
            return Failure(FileOperationError(
                f"Source file not found: {source}",
                context={"source": str(source), "destination": str(destination), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(FileOperationError(
                f"Permission denied moving file from {source} to {destination}",
                context={"source": str(source), "destination": str(destination), "error": str(e)}
            ))
        except shutil.Error as e:
            return Failure(FileOperationError(
                f"Failed to move file from {source} to {destination}",
                context={"source": str(source), "destination": str(destination), "error": str(e)}
            ))
        except Exception as e:
            return Failure(FileOperationError(
                f"Failed to move file from {source} to {destination}",
                context={
                    "source": str(source),
                    "destination": str(destination),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ))
    
    def delete_file(self, path: Path) -> Result[None]:
        """Delete file.
        
        Args:
            path: Path to file to delete
            
        Returns:
            Result[None]: Success or error
        """
        try:
            # Check if it's a directory first
            if path.is_dir():
                return Failure(FileOperationError(
                    f"Path is a directory, not a file: {path}",
                    context={"path": str(path)}
                ))
            
            path.unlink()
            return Success(None)
        except FileNotFoundError as e:
            return Failure(FileOperationError(
                f"File not found: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(FileOperationError(
                f"Permission denied deleting file: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except IsADirectoryError as e:
            return Failure(FileOperationError(
                f"Path is a directory, not a file: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(FileOperationError(
                f"Failed to delete file: {path}",
                context={"path": str(path), "error": str(e), "error_type": type(e).__name__}
            ))
    
    def file_exists(self, path: Path) -> bool:
        """Check if file exists.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return path.is_file()
    
    def get_file_size(self, path: Path) -> Result[int]:
        """Get file size in bytes.
        
        Args:
            path: Path to file
            
        Returns:
            Result[int]: File size on success, error on failure
        """
        try:
            size = path.stat().st_size
            return Success(size)
        except FileNotFoundError as e:
            return Failure(FileOperationError(
                f"File not found: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except PermissionError as e:
            return Failure(FileOperationError(
                f"Permission denied accessing file: {path}",
                context={"path": str(path), "error": str(e)}
            ))
        except Exception as e:
            return Failure(FileOperationError(
                f"Failed to get file size: {path}",
                context={"path": str(path), "error": str(e), "error_type": type(e).__name__}
            ))
