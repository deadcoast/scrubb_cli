"""Conflict resolution for file naming conflicts.

This module provides functionality to resolve file naming conflicts by
generating unique names using numeric suffixes while preserving file extensions.
"""

from pathlib import Path


class ConflictResolver:
    """Resolves file naming conflicts by generating unique names.
    
    When a file name conflict is detected, this resolver generates a unique
    name by appending a numeric suffix before the file extension.
    
    Example:
        >>> resolver = ConflictResolver()
        >>> existing = {Path("/dest/file.txt")}
        >>> resolved = resolver.resolve(Path("/dest/file.txt"), existing)
        >>> print(resolved)
        /dest/file_1.txt
    """
    
    def resolve(self, path: Path, existing: set[Path]) -> Path:
        """Resolve name conflict by generating unique name.
        
        Generates a unique file name by appending numeric suffixes (_1, _2, etc.)
        before the file extension. Efficiently handles multiple conflicts by
        incrementing the suffix until a unique name is found.
        
        Args:
            path: The original path that has a conflict
            existing: Set of existing paths to check against
            
        Returns:
            A unique Path that doesn't exist in the existing set
            
        Example:
            If path is "/dest/file.txt" and existing contains that path,
            returns "/dest/file_1.txt". If that also exists, returns
            "/dest/file_2.txt", and so on.
        """
        # If no conflict, return original path
        if path not in existing:
            return path
        
        # Extract components
        parent = path.parent
        stem = path.stem  # filename without extension
        suffix = path.suffix  # extension including the dot
        
        # Find unique name with numeric suffix
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            
            if new_path not in existing:
                return new_path
            
            counter += 1
