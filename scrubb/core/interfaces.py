"""Core interfaces for scrubb architecture.

This module defines all the protocols (interfaces) that components must implement.
Using protocols enables dependency injection and makes testing easier.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, List, Dict
from enum import Enum


class FileCategory(Enum):
    """Categories for file organization."""
    IMAGE = "Images"
    VIDEO = "Video"
    MARKDOWN = "Docs/Markdown"
    DOCUMENT = "Docs/Other Docs"
    DEVELOPMENT = "Development"
    OTHER = "Other"


class FileOperations(Protocol):
    """Interface for file I/O operations.
    
    All file operations return Result types to handle errors explicitly.
    """
    
    @abstractmethod
    def read_file(self, path: Path):
        """Read file content.
        
        Args:
            path: Path to file to read
            
        Returns:
            Result[str]: File content on success, error on failure
        """
        ...
    
    @abstractmethod
    def write_file(self, path: Path, content: str):
        """Write content to file.
        
        Args:
            path: Path to file to write
            content: Content to write
            
        Returns:
            Result[None]: Success or error
        """
        ...
    
    @abstractmethod
    def move_file(self, source: Path, destination: Path):
        """Move file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Result[None]: Success or error
        """
        ...
    
    @abstractmethod
    def delete_file(self, path: Path):
        """Delete file.
        
        Args:
            path: Path to file to delete
            
        Returns:
            Result[None]: Success or error
        """
        ...
    
    @abstractmethod
    def file_exists(self, path: Path) -> bool:
        """Check if file exists.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        ...
    
    @abstractmethod
    def get_file_size(self, path: Path):
        """Get file size in bytes.
        
        Args:
            path: Path to file
            
        Returns:
            Result[int]: File size on success, error on failure
        """
        ...


class DirectoryOperations(Protocol):
    """Interface for directory I/O operations.
    
    All directory operations return Result types to handle errors explicitly.
    """
    
    @abstractmethod
    def create_directory(self, path: Path):
        """Create directory.
        
        Args:
            path: Path to directory to create
            
        Returns:
            Result[None]: Success or error
        """
        ...
    
    @abstractmethod
    def remove_directory(self, path: Path):
        """Remove empty directory.
        
        Args:
            path: Path to directory to remove
            
        Returns:
            Result[None]: Success or error
        """
        ...
    
    @abstractmethod
    def list_directory(self, path: Path):
        """List directory contents.
        
        Args:
            path: Path to directory to list
            
        Returns:
            Result[List[Path]]: List of paths on success, error on failure
        """
        ...
    
    @abstractmethod
    def is_empty(self, path: Path):
        """Check if directory is empty.
        
        This should be O(1) - just check if any entry exists.
        
        Args:
            path: Path to directory to check
            
        Returns:
            Result[bool]: True if empty on success, error on failure
        """
        ...
    
    @abstractmethod
    def directory_exists(self, path: Path) -> bool:
        """Check if directory exists.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if directory exists, False otherwise
        """
        ...


class FileClassifier(Protocol):
    """Interface for file classification.
    
    Classifies files into categories based on their properties (typically extension).
    """
    
    @abstractmethod
    def classify(self, path: Path) -> FileCategory:
        """Classify file by extension.
        
        Args:
            path: Path to file to classify
            
        Returns:
            FileCategory: Category for the file
        """
        ...
    
    @abstractmethod
    def get_category_name(self, category: FileCategory) -> str:
        """Get display name for category.
        
        Args:
            category: Category to get name for
            
        Returns:
            str: Display name for category
        """
        ...


class ConflictResolver(Protocol):
    """Interface for name conflict resolution.
    
    Resolves conflicts when multiple files would have the same destination path.
    """
    
    @abstractmethod
    def resolve(self, path: Path, existing: set[Path]) -> Path:
        """Resolve name conflict by generating unique name.
        
        Args:
            path: Original path that conflicts
            existing: Set of existing paths to avoid
            
        Returns:
            Path: New unique path that doesn't conflict
        """
        ...


class TreeRenderer(Protocol):
    """Interface for tree rendering.
    
    Renders directory tree structures to string format.
    """
    
    @abstractmethod
    def render(self, snapshot, title: str) -> str:
        """Render directory tree to string.
        
        Args:
            snapshot: Directory snapshot to render
            title: Title for the tree
            
        Returns:
            str: Rendered tree as string
        """
        ...


class PathValidator(Protocol):
    """Interface for path validation.
    
    Validates paths for security and correctness.
    """
    
    @abstractmethod
    def validate(self, path: Path, root: Path):
        """Validate path is within root and safe.
        
        Args:
            path: Path to validate
            root: Root path that path must be within
            
        Returns:
            Result[Path]: Validated path on success, error on failure
        """
        ...
    
    @abstractmethod
    def resolve(self, path: str, root: Path):
        """Resolve and validate user-provided path.
        
        Args:
            path: User-provided path string
            root: Root path for validation
            
        Returns:
            Result[Path]: Resolved and validated path on success, error on failure
        """
        ...
