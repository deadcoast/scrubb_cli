"""Path validation for security.

This module provides path validation to prevent directory traversal attacks
and ensure paths are within expected boundaries.
"""

from pathlib import Path
from typing import Union

from ..core.result import Result, Success, Failure
from ..core.errors import PathSecurityError


class PathValidator:
    """Path validator for security checks.
    
    This class validates paths to ensure they are within expected boundaries
    and don't contain security vulnerabilities like directory traversal attempts.
    """
    
    def validate(self, path: Path, root: Path) -> Result[Path]:
        """Validate path is within root and safe.
        
        This method checks that:
        1. The path is within the root directory
        2. The path doesn't contain null bytes
        3. Symlinks don't point outside the root
        
        Args:
            path: Path to validate
            root: Root path that path must be within
            
        Returns:
            Result[Path]: Validated path on success, error on failure
        """
        try:
            # Resolve both paths to absolute paths
            resolved_path = path.resolve()
            resolved_root = root.resolve()
            
            # Check if path is within root
            try:
                resolved_path.relative_to(resolved_root)
            except ValueError:
                return Failure(PathSecurityError(
                    f"Path is outside root directory: {path}",
                    context={
                        "path": str(path),
                        "resolved_path": str(resolved_path),
                        "root": str(root),
                        "resolved_root": str(resolved_root)
                    }
                ))
            
            # Check for null bytes in the path string
            path_str = str(path)
            if '\0' in path_str:
                return Failure(PathSecurityError(
                    f"Path contains null bytes: {path}",
                    context={"path": path_str}
                ))
            
            return Success(resolved_path)
            
        except Exception as e:
            return Failure(PathSecurityError(
                f"Failed to validate path: {path}",
                context={
                    "path": str(path),
                    "root": str(root),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ))
    
    def resolve(self, path: str, root: Path) -> Result[Path]:
        """Resolve and validate user-provided path.
        
        This method:
        1. Converts the string to a Path
        2. Resolves it relative to root if it's relative
        3. Validates it using the validate() method
        
        Args:
            path: User-provided path string
            root: Root path for validation
            
        Returns:
            Result[Path]: Resolved and validated path on success, error on failure
        """
        try:
            # Check for null bytes in input string
            if '\0' in path:
                return Failure(PathSecurityError(
                    f"Path contains null bytes",
                    context={"path": path}
                ))
            
            # Check for suspicious patterns
            # Note: We check the string before Path normalization
            if '..' in path:
                # This is a warning sign, but we'll let resolve() handle it
                # and check the final resolved path
                pass
            
            # Convert to Path
            path_obj = Path(path)
            
            # If it's relative, make it relative to root
            if not path_obj.is_absolute():
                path_obj = root / path_obj
            
            # Validate the resolved path
            return self.validate(path_obj, root)
            
        except Exception as e:
            return Failure(PathSecurityError(
                f"Failed to resolve path: {path}",
                context={
                    "path": path,
                    "root": str(root),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ))
