"""File organization business logic.

This module provides pure business logic for organizing files into categories
with efficient O(n) algorithms for planning and execution.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from ..core.result import Result, Success, Failure, OperationResult
from ..core.errors import FileOperationError, DirectoryOperationError
from ..core.interfaces import FileOperations, DirectoryOperations, FileClassifier, ConflictResolver


@dataclass
class OrganizationPlan:
    """Plan for organizing files.
    
    Attributes:
        files_to_move: List of (source, destination) tuples for file moves
        directories_to_create: Set of directories that need to be created
        directories_to_remove: List of directories to remove (ordered bottom-up)
        conflicts: Dictionary mapping original paths to resolved paths
    """
    files_to_move: list[tuple[Path, Path]] = field(default_factory=list)
    directories_to_create: set[Path] = field(default_factory=set)
    directories_to_remove: list[Path] = field(default_factory=list)
    conflicts: dict[Path, Path] = field(default_factory=dict)


class FileOrganizer:
    """Pure business logic for file organization.
    
    This class implements efficient O(n) algorithms for:
    - Planning file organization without filesystem changes
    - Executing organization plans
    - Detecting empty directories
    - Resolving naming conflicts
    
    All dependencies are injected for testability.
    """
    
    def __init__(
        self,
        file_ops: FileOperations,
        dir_ops: DirectoryOperations,
        classifier: FileClassifier,
        conflict_resolver: ConflictResolver,
    ):
        """Initialize organizer with dependencies.
        
        Args:
            file_ops: File operations interface
            dir_ops: Directory operations interface
            classifier: File classifier interface
            conflict_resolver: Conflict resolver interface
        """
        self.file_ops = file_ops
        self.dir_ops = dir_ops
        self.classifier = classifier
        self.conflict_resolver = conflict_resolver
    
    def plan_organization(
        self,
        root: Path,
        scrubbed_folder: Path,
    ) -> Result[OrganizationPlan]:
        """Plan file organization without making changes.
        
        This is O(n) where n is the number of files.
        Uses a single-pass traversal to collect all files and directories,
        then performs bottom-up empty directory detection.
        
        Args:
            root: Root directory to organize
            scrubbed_folder: Destination folder for organized files
            
        Returns:
            Result containing OrganizationPlan on success, or error on failure
        """
        plan = OrganizationPlan()
        
        # Single pass: collect all files and directories
        files_by_dir: dict[Path, list[Path]] = {}
        all_dirs: set[Path] = set()
        
        try:
            for item in root.rglob("*"):
                if item.is_file():
                    # Skip files already in scrubbed folder
                    if self._is_in_scrubbed_folder(item, scrubbed_folder):
                        continue
                    
                    # Classify and plan move
                    category = self.classifier.classify(item)
                    dest_dir = scrubbed_folder / category.value
                    dest_path = dest_dir / item.name
                    
                    # Track files by parent directory
                    parent = item.parent
                    if parent not in files_by_dir:
                        files_by_dir[parent] = []
                    files_by_dir[parent].append(item)
                    
                    # Add to plan
                    plan.files_to_move.append((item, dest_path))
                    plan.directories_to_create.add(dest_dir)
                
                elif item.is_dir():
                    all_dirs.add(item)
        
        except Exception as e:
            return Failure(FileOperationError(
                "Failed to scan directory",
                context={"root": str(root), "error": str(e)}
            ))
        
        # Resolve conflicts (O(n) where n is number of files)
        existing_destinations: set[Path] = set()
        resolved_moves: list[tuple[Path, Path]] = []
        
        for source, dest in plan.files_to_move:
            if dest in existing_destinations:
                # Conflict - resolve it
                resolved_dest = self.conflict_resolver.resolve(dest, existing_destinations)
                plan.conflicts[dest] = resolved_dest
                resolved_moves.append((source, resolved_dest))
                existing_destinations.add(resolved_dest)
            else:
                resolved_moves.append((source, dest))
                existing_destinations.add(dest)
        
        plan.files_to_move = resolved_moves
        
        # Identify empty directories (O(d) where d is number of directories)
        # Bottom-up traversal ensures we check children before parents
        sorted_dirs = sorted(all_dirs, key=lambda p: len(p.parts), reverse=True)
        
        for dir_path in sorted_dirs:
            if dir_path == root or self._is_in_scrubbed_folder(dir_path, scrubbed_folder):
                continue
            
            # Check if directory will be empty after moves
            if self._will_be_empty(dir_path, files_by_dir):
                plan.directories_to_remove.append(dir_path)
        
        return Success(plan)
    
    def execute_plan(self, plan: OrganizationPlan) -> OperationResult:
        """Execute organization plan.
        
        This is O(n) where n is the number of operations.
        
        Args:
            plan: The organization plan to execute
            
        Returns:
            OperationResult with statistics and any errors
        """
        result = OperationResult(
            files_moved=0,
            files_by_category={},
            empty_folders_removed=0,
            critical_errors=[],
            warnings=[],
        )
        
        # Create directories
        for dir_path in plan.directories_to_create:
            create_result = self.dir_ops.create_directory(dir_path)
            if create_result.is_failure():
                result.warnings.append(create_result.error)
        
        # Move files
        for source, dest in plan.files_to_move:
            move_result = self.file_ops.move_file(source, dest)
            
            if move_result.is_success():
                result.files_moved += 1
                
                # Update category count
                category = self.classifier.classify(source)
                category_name = category.value
                result.files_by_category[category_name] = \
                    result.files_by_category.get(category_name, 0) + 1
            else:
                result.critical_errors.append(move_result.error)
        
        # Remove empty directories
        for dir_path in plan.directories_to_remove:
            remove_result = self.dir_ops.remove_directory(dir_path)
            
            if remove_result.is_success():
                result.empty_folders_removed += 1
            else:
                result.warnings.append(remove_result.error)
        
        return result
    
    def _is_in_scrubbed_folder(self, path: Path, scrubbed_folder: Path) -> bool:
        """Check if path is within scrubbed folder.
        
        Args:
            path: Path to check
            scrubbed_folder: The scrubbed folder path
            
        Returns:
            True if path is within scrubbed folder, False otherwise
        """
        try:
            path.relative_to(scrubbed_folder)
            return True
        except ValueError:
            return False
    
    def _will_be_empty(
        self,
        dir_path: Path,
        files_by_dir: dict[Path, list[Path]],
    ) -> bool:
        """Check if directory will be empty after moves.
        
        This is O(1) per directory when called in bottom-up order.
        
        Args:
            dir_path: Directory to check
            files_by_dir: Dictionary mapping directories to their files
            
        Returns:
            True if directory will be empty after moves, False otherwise
        """
        # If directory has files that won't be moved, it won't be empty
        if dir_path in files_by_dir and files_by_dir[dir_path]:
            return False
        
        # Check if any subdirectories won't be empty
        for subdir in files_by_dir:
            try:
                # Check if subdir is a child of dir_path
                subdir.relative_to(dir_path)
                if subdir != dir_path:
                    if not self._will_be_empty(subdir, files_by_dir):
                        return False
            except ValueError:
                # subdir is not relative to dir_path, skip it
                continue
        
        return True
