"""Folder organization module for categorizing and organizing files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union
import shutil

from scrubb.file_classifier import FileCategory, FileClassifier


@dataclass
class OrganizationStats:
    """Statistics for folder organization operations."""
    files_moved: int = 0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    empty_folders_removed: int = 0
    errors: int = 0
    error_files: List[str] = field(default_factory=list)
    directory_permission_warnings: int = 0  # Separate counter for non-critical warnings


@dataclass
class FileOperation:
    """Represents a planned file move operation in dry-run mode."""
    source: Path
    destination: Path
    category: FileCategory
    is_conflict: bool = False
    resolved_name: Optional[str] = None


@dataclass
class ConflictInfo:
    """Information about a name conflict and its resolution."""
    original_name: str
    resolved_name: str
    category: str
    destination_path: Path


@dataclass
class SkippedFile:
    """Information about a file that was skipped during organization."""
    path: Path
    reason: str


@dataclass
class DryRunStats:
    """Extended statistics for dry-run mode operations."""
    files_to_move: int = 0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    empty_folders_to_remove: int = 0
    file_operations: List[FileOperation] = field(default_factory=list)
    directories_to_create: List[Path] = field(default_factory=list)
    directories_to_remove: List[Path] = field(default_factory=list)
    conflicts: List[ConflictInfo] = field(default_factory=list)
    skipped_files: List[SkippedFile] = field(default_factory=list)
    potential_errors: List[str] = field(default_factory=list)


class FolderOrganizer:
    """Organizes files into categorized folders and removes empty directories."""
    
    # Common hidden/system files that should be ignored/removed
    IGNORED_FILES = {
        '.DS_Store',      # macOS
        'Thumbs.db',      # Windows
        'desktop.ini',    # Windows
        '.gitkeep',       # Git
        '.gitignore',     # Git (in empty dirs)
        '.keep',          # Generic keep file
    }
    
    @staticmethod
    def _is_onedrive_path(path: Path) -> bool:
        """
        Check if a path is within OneDrive.
        
        OneDrive paths typically contain 'OneDrive' in the path.
        This helps identify cloud-synced directories that may have special permissions.
        
        Args:
            path: Path to check
            
        Returns:
            True if path appears to be in OneDrive
        """
        path_str = str(path).lower()
        return 'onedrive' in path_str
    
    def __init__(self, root_path: Path, classifier: FileClassifier, dry_run: bool = False):
        """
        Initialize the folder organizer.
        
        Args:
            root_path: Root directory to organize
            classifier: FileClassifier instance for categorizing files
            dry_run: If True, simulate operations without making changes
        """
        self.root_path = root_path.resolve()
        self.scrubbed_path = self.root_path / "Scrubbed"
        self.classifier = classifier
        self.dry_run = dry_run
        self.stats = OrganizationStats()
    
    def organize(self) -> Union[OrganizationStats, DryRunStats]:
        """
        Main entry point for organization process.
        
        Returns:
            DryRunStats if dry_run=True, OrganizationStats otherwise
        """
        if self.dry_run:
            return self._organize_dry_run()
        else:
            return self._organize_actual()
    

    
    def _organize_actual(self) -> OrganizationStats:
        """
        Perform actual file organization with file system modifications.
        
        Returns:
            OrganizationStats with results of the organization
        """
        from .verbosity import VerbosityManager
        import typer
        
        verbosity_manager = VerbosityManager.get_current()
        
        # Create Scrubbed folder if it doesn't exist
        self.scrubbed_path.mkdir(exist_ok=True)
        
        # Scan all files
        files = self._scan_files()
        
        # Move each file to its category folder
        for file_path in files:
            category = self.classifier.classify(file_path)
            
            # Log category assignment in verbose mode (Requirements 4.3)
            if verbosity_manager.should_print_debug():
                typer.echo(f"  {file_path.name} → {category.value}")
            
            self._move_file(file_path, category)
        
        # Remove empty folders
        removed_count = self._remove_empty_folders()
        self.stats.empty_folders_removed = removed_count
        
        # Log completion statistics (Requirements 4.5)
        if verbosity_manager.should_print_info():
            typer.echo(f"\nOperation complete: {self.stats.files_moved} files moved, {self.stats.empty_folders_removed} empty folders removed")
        
        return self.stats
    
    def _organize_dry_run(self) -> DryRunStats:
        """
        Simulate organization without making file system changes.
        
        Returns:
            DryRunStats with detailed information about what would happen
        """
        from .verbosity import VerbosityManager
        import typer
        
        verbosity_manager = VerbosityManager.get_current()
        
        stats = DryRunStats()
        simulated_destinations = set()  # Track simulated file destinations
        
        # Scan files using existing method
        files = self._scan_files()
        
        # Classify and simulate operations for each file
        for file_path in files:
            category = self.classifier.classify(file_path)
            
            # Log category assignment in verbose mode (Requirements 4.3)
            if verbosity_manager.should_print_debug():
                typer.echo(f"  {file_path.name} → {category.value}")
            
            # Simulate destination path
            dest_path = self._simulate_destination(file_path, category)
            
            # Check for conflicts
            is_conflict = self._would_conflict(dest_path, simulated_destinations)
            resolved_name = None
            
            if is_conflict:
                # Simulate conflict resolution
                resolved_path = self._simulate_conflict_resolution(
                    dest_path, simulated_destinations
                )
                resolved_name = resolved_path.name
                
                # Track conflict information
                stats.conflicts.append(
                    ConflictInfo(
                        original_name=file_path.name,
                        resolved_name=resolved_name,
                        category=category.value,
                        destination_path=resolved_path
                    )
                )
                
                dest_path = resolved_path
            
            # Add to simulated destinations
            simulated_destinations.add(dest_path)
            
            # Record file operation
            stats.file_operations.append(
                FileOperation(
                    source=file_path,
                    destination=dest_path,
                    category=category,
                    is_conflict=is_conflict,
                    resolved_name=resolved_name
                )
            )
            
            # Update statistics
            stats.files_to_move += 1
            category_name = category.value
            stats.files_by_category[category_name] = \
                stats.files_by_category.get(category_name, 0) + 1
            
            # Track directories that would be created
            if dest_path.parent not in stats.directories_to_create:
                stats.directories_to_create.append(dest_path.parent)
        
        # Identify empty directories that would be removed
        stats.directories_to_remove = self._identify_empty_directories(files)
        stats.empty_folders_to_remove = len(stats.directories_to_remove)
        
        # Check for potential errors
        stats.potential_errors = self._check_potential_errors(files)
        
        return stats
    
    def _scan_files(self) -> List[Path]:
        """
        Recursively find all files in root_path.
        
        Returns:
            List of Path objects for all files found
        """
        from .verbosity import VerbosityManager
        
        files = []
        
        # Use rglob to recursively find all files
        for item in self.root_path.rglob("*"):
            # Skip if it's not a file
            if not item.is_file():
                continue
            
            # Skip files already in the Scrubbed folder
            try:
                item.relative_to(self.scrubbed_path)
                continue  # File is in Scrubbed folder, skip it
            except ValueError:
                # File is not in Scrubbed folder, include it
                files.append(item)
        
        # Log number of files discovered (Requirements 4.2)
        verbosity_manager = VerbosityManager.get_current()
        if verbosity_manager.should_print_info():
            import typer
            typer.echo(f"Files discovered: {len(files)}")
        
        return files
    
    def _move_file(self, file_path: Path, category: FileCategory) -> bool:
        """
        Move a file to its category folder.
        
        Args:
            file_path: Path to the file to move
            category: FileCategory for the file
            
        Returns:
            True if successful, False if error occurred
        """
        try:
            # Create category directory path
            category_dir = self.scrubbed_path / category.value
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine destination path
            dest_path = category_dir / file_path.name
            
            # Handle name conflicts
            if dest_path.exists():
                dest_path = self._handle_name_conflict(dest_path)
            
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            
            # Update statistics
            self.stats.files_moved += 1
            category_name = category.value
            self.stats.files_by_category[category_name] = \
                self.stats.files_by_category.get(category_name, 0) + 1
            
            return True
            
        except PermissionError as e:
            # File move permission errors are CRITICAL
            self.stats.errors += 1
            self.stats.error_files.append(f"Permission denied: {file_path}")
            return False
        except OSError as e:
            # Other file move errors are also CRITICAL
            self.stats.errors += 1
            self.stats.error_files.append(f"Failed to move {file_path}: {str(e)}")
            return False
    
    def _simulate_destination(self, file_path: Path, category: FileCategory) -> Path:
        """
        Calculate where a file would be moved in dry-run mode.
        
        Args:
            file_path: Path to the file
            category: FileCategory for the file
            
        Returns:
            Path where the file would be moved
        """
        category_dir = self.scrubbed_path / category.value
        return category_dir / file_path.name
    
    def _would_conflict(self, dest_path: Path, simulated_destinations: set) -> bool:
        """
        Check if destination would conflict without file system access.
        
        Args:
            dest_path: Destination path to check
            simulated_destinations: Set of already simulated destination paths
            
        Returns:
            True if conflict would occur, False otherwise
        """
        # Check if file already exists on disk
        if dest_path.exists():
            return True
        
        # Check if we've already simulated moving a file to this destination
        if dest_path in simulated_destinations:
            return True
        
        return False
    
    def _simulate_conflict_resolution(self, dest_path: Path, simulated_destinations: set) -> Path:
        """
        Generate resolved filename for conflicts without file system access.
        
        Args:
            dest_path: Original destination path
            simulated_destinations: Set of already simulated destination paths
            
        Returns:
            Resolved Path that doesn't conflict
        """
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        # Try incrementing numbers until we find a unique name
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            # Check both file system and simulated destinations
            if not new_path.exists() and new_path not in simulated_destinations:
                return new_path
            counter += 1
    
    def _handle_name_conflict(self, dest_path: Path) -> Path:
        """
        Generate a unique filename if conflict exists.
        
        Args:
            dest_path: Original destination path
            
        Returns:
            Unique Path that doesn't conflict
        """
        # Extract stem and suffix
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        # Try incrementing numbers until we find a unique name
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _remove_empty_folders(self) -> int:
        """
        Remove all empty directories, return count removed.
        
        Returns:
            Number of directories removed
        """
        removed_count = 0
        
        # Use bottom-up traversal to handle nested empty directories
        # Walk the directory tree from bottom to top
        for dirpath, dirnames, filenames in sorted(
            self.root_path.walk(top_down=False), 
            key=lambda x: str(x[0]), 
            reverse=True
        ):
            dir_path = Path(dirpath)
            
            # Skip root directory
            if dir_path == self.root_path:
                continue
            
            # Skip Scrubbed folder and its subdirectories
            try:
                dir_path.relative_to(self.scrubbed_path)
                continue
            except ValueError:
                pass
            
            # Check if directory is empty
            if self._is_empty_directory(dir_path):
                # Skip OneDrive directories - they have special permissions and reparse points
                if self._is_onedrive_path(dir_path):
                    self.stats.directory_permission_warnings += 1
                    continue
                
                try:
                    # Remove any ignored files first
                    for item in dir_path.iterdir():
                        if item.is_file() and item.name in self.IGNORED_FILES:
                            try:
                                item.unlink()
                            except (PermissionError, OSError):
                                pass
                    
                    # Now remove the directory
                    dir_path.rmdir()
                    removed_count += 1
                except PermissionError as e:
                    # Permission errors on directory removal are NON-CRITICAL
                    # This commonly happens with cloud storage or system-protected folders
                    # These are warnings, not errors - the operation succeeded for accessible files
                    self.stats.directory_permission_warnings += 1
                    # Don't add to error_files - these aren't critical failures
                except OSError as e:
                    # Other OS errors during directory removal (also non-critical)
                    # Could be reparse points, junctions, or other special directories
                    self.stats.directory_permission_warnings += 1
        
        return removed_count
    
    def _identify_empty_directories(self, files: List[Path]) -> List[Path]:
        """
        Simulate which directories would become empty after file moves.
        
        Args:
            files: List of files that would be moved
            
        Returns:
            List of directories that would be removed
        """
        empty_dirs = []
        
        # Walk the directory tree from bottom to top (like _remove_empty_folders)
        # This ensures we catch parent directories that become empty after subdirectories are removed
        for dirpath, dirnames, filenames in sorted(
            self.root_path.walk(top_down=False), 
            key=lambda x: str(x[0]), 
            reverse=True
        ):
            dir_path = Path(dirpath)
            
            # Skip root directory
            if dir_path == self.root_path:
                continue
            
            # Skip Scrubbed folder and its subdirectories
            try:
                dir_path.relative_to(self.scrubbed_path)
                continue
            except ValueError:
                pass
            
            # Check if directory would be empty after moves
            if self._would_be_empty_after_moves(dir_path, files):
                empty_dirs.append(dir_path)
        
        return empty_dirs
    
    def _would_be_empty_after_moves(self, dir_path: Path, files_to_move: List[Path]) -> bool:
        """
        Check if directory would be empty after moving specified files.
        
        Args:
            dir_path: Directory to check
            files_to_move: List of files that would be moved
            
        Returns:
            True if directory would be empty after moves
        """
        try:
            items = list(dir_path.iterdir())
            
            # If no items, it's empty
            if not items:
                return True
            
            # Check each item
            for item in items:
                if item.is_file():
                    # Ignore common hidden/system files
                    if item.name in self.IGNORED_FILES:
                        continue
                    
                    # If file would be moved, ignore it
                    if item in files_to_move:
                        continue
                    # File would remain, directory not empty
                    return False
                elif item.is_dir():
                    # Check if subdirectory would be empty
                    if not self._would_be_empty_after_moves(item, files_to_move):
                        return False
            
            # All items would be moved, are empty subdirectories, or are ignored files
            return True
            
        except (PermissionError, OSError):
            return False
    
    def _check_potential_errors(self, files: List[Path]) -> List[str]:
        """
        Check for potential errors that might occur during actual execution.
        
        Args:
            files: List of files to check
            
        Returns:
            List of error messages for potential issues
        """
        errors = []
        
        for file_path in files:
            try:
                # Check read permissions by attempting to stat the file
                file_path.stat()
            except PermissionError:
                errors.append(f"Permission denied: {file_path}")
            except FileNotFoundError:
                errors.append(f"File not found: {file_path}")
            except OSError as e:
                errors.append(f"Error accessing {file_path}: {str(e)}")
            except Exception as e:
                errors.append(f"Unexpected error with {file_path}: {str(e)}")
        
        return errors
    
    def _is_empty_directory(self, dir_path: Path) -> bool:
        """
        Check if directory is empty or contains only empty subdirs and ignored files.
        
        Args:
            dir_path: Directory to check
            
        Returns:
            True if empty or contains only empty subdirectories and ignored files
        """
        try:
            # Check if directory has any items
            items = list(dir_path.iterdir())
            
            # If no items, it's empty
            if not items:
                return True
            
            # If it has items, check if they're all empty directories or ignored files
            for item in items:
                if item.is_file():
                    # Ignore common hidden/system files
                    if item.name in self.IGNORED_FILES:
                        continue
                    # Found a real file, directory is not empty
                    return False
                if item.is_dir() and not self._is_empty_directory(item):
                    return False
            
            # All items are either empty directories or ignored files
            return True
            
        except (PermissionError, OSError):
            return False


class DryRunFormatter:
    """Formatter for dry-run mode output."""
    
    @staticmethod
    def format_output(stats: DryRunStats, root_path: Path) -> str:
        """
        Format dry-run statistics into readable output.
        
        Args:
            stats: DryRunStats object with operation details
            root_path: Root directory being analyzed
            
        Returns:
            Formatted string with all dry-run information
        """
        output = []
        
        # Header section with dry-run indicator
        output.append("\n" + "=" * 70)
        output.append("DRY RUN PREVIEW - No changes will be made")
        output.append("=" * 70 + "\n")
        
        # Summary statistics section
        output.append(" SUMMARY")
        output.append(f"  Files to move: {stats.files_to_move}")
        output.append(f"  Directories to create: {len(stats.directories_to_create)}")
        output.append(f"  Empty directories to remove: {stats.empty_folders_to_remove}")
        output.append(f"  Files to skip: {len(stats.skipped_files)}")
        output.append(f"  Potential conflicts: {len(stats.conflicts)}")
        
        # Files by category section
        if stats.files_by_category:
            output.append("\n FILES BY CATEGORY")
            for category, count in sorted(stats.files_by_category.items()):
                output.append(f"  {category}: {count} files")
        
        # Directories to create section
        if stats.directories_to_create:
            output.append("\n DIRECTORIES TO CREATE")
            for dir_path in sorted(stats.directories_to_create):
                output.append(f"  {dir_path}")
        
        # File operations section grouped by category
        if stats.file_operations:
            output.append("\n FILE OPERATIONS")
            by_category = {}
            for op in stats.file_operations:
                cat = op.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(op)
            
            for category, operations in sorted(by_category.items()):
                output.append(f"\n  {category}:")
                for op in operations:
                    conflict_marker = " [CONFLICT RESOLVED]" if op.is_conflict else ""
                    output.append(f"    {op.source.name} → {op.destination}{conflict_marker}")
        
        # Conflicts section
        if stats.conflicts:
            output.append("\n  NAME CONFLICTS")
            for conflict in stats.conflicts:
                output.append(f"  {conflict.original_name} → {conflict.resolved_name}")
                output.append(f"    Category: {conflict.category}")
        
        # Skipped files section
        if stats.skipped_files:
            output.append("\n⏭  SKIPPED FILES")
            for skipped in stats.skipped_files:
                output.append(f"  {skipped.path} - {skipped.reason}")
        
        # Empty directories to remove section
        if stats.directories_to_remove:
            output.append("\n  EMPTY DIRECTORIES TO REMOVE")
            for dir_path in sorted(stats.directories_to_remove):
                output.append(f"  {dir_path}")
        
        # Potential errors section
        if stats.potential_errors:
            output.append("\n POTENTIAL ERRORS")
            for error in stats.potential_errors:
                output.append(f"  {error}")
        else:
            output.append("\n No potential errors detected")
        
        # Footer with reminder that no changes were made
        output.append("\n" + "=" * 70)
        output.append("This was a DRY RUN - No files were moved or modified")
        output.append("Run without --dry flag to execute these changes")
        output.append("=" * 70 + "\n")
        
        return "\n".join(output)
