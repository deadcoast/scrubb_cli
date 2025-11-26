"""Tree building and simulation for directory structures.

This module provides functionality to build directory tree structures and
simulate the after-state of file organization operations without filesystem access.
"""

from pathlib import Path
from typing import Protocol
from ..tree_models import DirectoryNode, DirectorySnapshot, DirectoryStatistics
from .classifier import FileCategory
from .organizer import OrganizationPlan
from datetime import datetime


class TreeBuilder:
    """Builds directory tree structures and simulates operations.
    
    This class provides:
    - Building DirectoryNode trees from filesystem
    - Simulating after-state without filesystem access
    - Efficient tree manipulation operations
    """
    
    def __init__(self, classifier: Protocol):
        """Initialize tree builder with classifier.
        
        Args:
            classifier: File classifier for categorizing files
        """
        self.classifier = classifier
    
    def build_tree(self, root: Path, max_depth: int | None = None) -> DirectorySnapshot:
        """Build directory tree from filesystem.
        
        Args:
            root: Root directory to build tree from
            max_depth: Maximum depth to traverse (None for unlimited)
            
        Returns:
            DirectorySnapshot containing the tree and statistics
        """
        root_node = self._build_node(root, depth=0, max_depth=max_depth)
        statistics = self._calculate_statistics(root_node)
        
        return DirectorySnapshot(
            root_path=root,
            root_node=root_node,
            statistics=statistics,
            timestamp=datetime.now(),
            is_simulated=False
        )
    
    def simulate_after_state(
        self,
        before_snapshot: DirectorySnapshot,
        plan: OrganizationPlan,
        scrubbed_folder: Path
    ) -> DirectorySnapshot:
        """Simulate after-state without filesystem access.
        
        This method simulates what the directory tree will look like after
        executing the organization plan, without making any filesystem changes.
        
        Args:
            before_snapshot: Snapshot of directory before organization
            plan: Organization plan to simulate
            scrubbed_folder: Path to the scrubbed folder
            
        Returns:
            DirectorySnapshot of simulated after-state
        """
        # Deep copy the tree structure
        simulated_root = self._deep_copy_node(before_snapshot.root_node)
        
        # Remove moved files from their original locations
        files_to_remove = {source for source, _ in plan.files_to_move}
        self._remove_moved_files(simulated_root, files_to_remove)
        
        # Add scrubbed folder with organized files
        self._add_scrubbed_folder(simulated_root, plan, scrubbed_folder, before_snapshot.root_path)
        
        # Remove empty directories
        dirs_to_remove = set(plan.directories_to_remove)
        self._remove_empty_dirs(simulated_root, dirs_to_remove)
        
        # Recalculate statistics
        statistics = self._calculate_statistics(simulated_root)
        
        return DirectorySnapshot(
            root_path=before_snapshot.root_path,
            root_node=simulated_root,
            statistics=statistics,
            timestamp=datetime.now(),
            is_simulated=True
        )
    
    def _build_node(self, path: Path, depth: int, max_depth: int | None) -> DirectoryNode:
        """Build a directory node recursively.
        
        Args:
            path: Path to build node from
            depth: Current depth in tree
            max_depth: Maximum depth to traverse
            
        Returns:
            DirectoryNode for the path
        """
        is_dir = path.is_dir()
        
        node = DirectoryNode(
            path=path,
            name=path.name,
            is_directory=is_dir,
            depth=depth,
            children=[]
        )
        
        if is_dir:
            # Stop if we've reached max depth
            if max_depth is not None and depth >= max_depth:
                return node
            
            # Add children
            try:
                for child_path in sorted(path.iterdir()):
                    child_node = self._build_node(child_path, depth + 1, max_depth)
                    node.children.append(child_node)
                    node.size += child_node.size
            except PermissionError:
                # Skip directories we can't read
                pass
        else:
            # File node
            try:
                node.size = path.stat().st_size
                node.category = self.classifier.classify(path)
            except (OSError, PermissionError):
                node.size = 0
        
        return node
    
    def _deep_copy_node(self, node: DirectoryNode) -> DirectoryNode:
        """Create a deep copy of a directory node.
        
        Args:
            node: Node to copy
            
        Returns:
            Deep copy of the node
        """
        copied = DirectoryNode(
            path=node.path,
            name=node.name,
            is_directory=node.is_directory,
            size=node.size,
            category=node.category,
            depth=node.depth,
            is_new=node.is_new,
            is_removed=node.is_removed,
            children=[]
        )
        
        # Recursively copy children
        for child in node.children:
            copied.children.append(self._deep_copy_node(child))
        
        return copied
    
    def _remove_moved_files(self, node: DirectoryNode, files_to_remove: set[Path]) -> None:
        """Remove moved files from tree.
        
        Args:
            node: Root node to remove files from
            files_to_remove: Set of file paths to remove
        """
        if not node.is_directory:
            return
        
        # Filter out removed files
        remaining_children = []
        for child in node.children:
            if child.path in files_to_remove:
                # Mark as removed but keep in tree for visualization
                child.is_removed = True
                node.size -= child.size
            else:
                if child.is_directory:
                    self._remove_moved_files(child, files_to_remove)
                remaining_children.append(child)
        
        node.children = remaining_children
    
    def _add_scrubbed_folder(
        self,
        root: DirectoryNode,
        plan: OrganizationPlan,
        scrubbed_folder: Path,
        root_path: Path
    ) -> None:
        """Add scrubbed folder with organized files to tree.
        
        Args:
            root: Root node to add scrubbed folder to
            plan: Organization plan
            scrubbed_folder: Path to scrubbed folder
            root_path: Root path of the tree
        """
        # Check if scrubbed folder already exists in tree
        scrubbed_node = None
        for child in root.children:
            if child.path == scrubbed_folder:
                scrubbed_node = child
                break
        
        # Create scrubbed folder node if it doesn't exist
        if scrubbed_node is None:
            scrubbed_node = DirectoryNode(
                path=scrubbed_folder,
                name=scrubbed_folder.name,
                is_directory=True,
                depth=root.depth + 1,
                is_new=True,
                children=[]
            )
            root.children.append(scrubbed_node)
        
        # Group files by category directory
        files_by_category: dict[Path, list[tuple[Path, Path]]] = {}
        for source, dest in plan.files_to_move:
            category_dir = dest.parent
            if category_dir not in files_by_category:
                files_by_category[category_dir] = []
            files_by_category[category_dir].append((source, dest))
        
        # Add category directories and files
        for category_dir, files in files_by_category.items():
            # Find or create category directory node
            category_node = None
            for child in scrubbed_node.children:
                if child.path == category_dir:
                    category_node = child
                    break
            
            if category_node is None:
                category_node = DirectoryNode(
                    path=category_dir,
                    name=category_dir.name,
                    is_directory=True,
                    depth=scrubbed_node.depth + 1,
                    is_new=True,
                    children=[]
                )
                scrubbed_node.children.append(category_node)
            
            # Add files to category directory
            for source, dest in files:
                # Get file size from source
                try:
                    file_size = source.stat().st_size if source.exists() else 0
                except (OSError, PermissionError):
                    file_size = 0
                
                file_node = DirectoryNode(
                    path=dest,
                    name=dest.name,
                    is_directory=False,
                    size=file_size,
                    category=self.classifier.classify(source),
                    depth=category_node.depth + 1,
                    is_new=True
                )
                category_node.children.append(file_node)
                category_node.size += file_size
            
            scrubbed_node.size += category_node.size
        
        root.size += scrubbed_node.size
    
    def _remove_empty_dirs(self, node: DirectoryNode, dirs_to_remove: set[Path]) -> None:
        """Remove empty directories from tree.
        
        Args:
            node: Root node to remove directories from
            dirs_to_remove: Set of directory paths to remove
        """
        if not node.is_directory:
            return
        
        # Recursively process children first
        for child in node.children:
            if child.is_directory:
                self._remove_empty_dirs(child, dirs_to_remove)
        
        # Filter out removed directories
        node.children = [
            child for child in node.children
            if not (child.is_directory and child.path in dirs_to_remove)
        ]
    
    def _calculate_statistics(self, root: DirectoryNode) -> DirectoryStatistics:
        """Calculate statistics for directory tree.
        
        Args:
            root: Root node to calculate statistics for
            
        Returns:
            DirectoryStatistics for the tree
        """
        stats = DirectoryStatistics()
        self._collect_statistics(root, stats)
        return stats
    
    def _collect_statistics(self, node: DirectoryNode, stats: DirectoryStatistics) -> None:
        """Recursively collect statistics from tree.
        
        Args:
            node: Current node
            stats: Statistics object to update
        """
        if node.is_directory:
            stats.total_directories += 1
            stats.max_depth = max(stats.max_depth, node.depth)
            
            for child in node.children:
                self._collect_statistics(child, stats)
        else:
            stats.total_files += 1
            stats.total_size += node.size
            
            if node.category:
                category_name = node.category.value
                stats.files_by_category[category_name] = \
                    stats.files_by_category.get(category_name, 0) + 1
                stats.size_by_category[category_name] = \
                    stats.size_by_category.get(category_name, 0) + node.size
