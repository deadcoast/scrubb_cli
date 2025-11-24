"""Tree visualization orchestrator for before/after directory comparisons."""

from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from scrubb.tree_models import DirectorySnapshot, DirectoryNode, DirectoryStatistics
from scrubb.directory_scanner import DirectoryScanner
from scrubb.tree_renderer import TreeRenderer
from scrubb.tree_comparator import TreeComparator
from scrubb.file_classifier import FileClassifier
from scrubb.folder_organizer import DryRunStats
from scrubb.statistics_calculator import StatisticsCalculator


class TreeVisualizer:
    """Main orchestrator for tree visualization functionality."""
    
    def __init__(self, root_path: Path, renderer: TreeRenderer):
        """Initialize with root directory and renderer.
        
        Args:
            root_path: Root directory to visualize
            renderer: TreeRenderer instance for rendering trees
        """
        self.root_path = root_path
        self.renderer = renderer
        
        # Initialize DirectoryScanner with FileClassifier
        classifier = FileClassifier()
        self.scanner = DirectoryScanner(classifier)
        self.classifier = classifier

    def capture_before_state(self) -> DirectorySnapshot:
        """Capture current directory state before operations.
        
        Returns:
            DirectorySnapshot of the current state
        """
        return self.scanner.scan(self.root_path)

    def capture_after_state(self) -> DirectorySnapshot:
        """Capture directory state after operations complete.
        
        Returns:
            DirectorySnapshot of the state after operations
        """
        return self.scanner.scan(self.root_path)

    def simulate_after_state(self, dry_run_stats: DryRunStats) -> DirectorySnapshot:
        """Simulate after state based on dry-run operation plan.
        
        Args:
            dry_run_stats: DryRunStats from dry-run execution
            
        Returns:
            DirectorySnapshot with simulated after state (is_simulated=True)
        """
        # Start with current directory tree
        current_snapshot = self.scanner.scan(self.root_path)
        root_node = current_snapshot.root_node
        
        # Create a simulated tree by:
        # 1. Removing files that would be moved
        # 2. Adding Scrubbed folder structure with moved files
        # 3. Removing empty directories
        
        # Build a set of files that would be moved
        files_to_move = {op.source for op in dry_run_stats.file_operations}
        
        # Build simulated root node
        simulated_root = self._simulate_tree_after_moves(
            root_node, 
            files_to_move,
            dry_run_stats.directories_to_remove
        )
        
        # Add Scrubbed folder structure
        self._add_scrubbed_folder_to_tree(simulated_root, dry_run_stats)
        
        # Calculate simulated statistics
        simulated_statistics = StatisticsCalculator.calculate(simulated_root, self.classifier)
        
        # Return simulated snapshot
        return DirectorySnapshot(
            root_path=self.root_path,
            root_node=simulated_root,
            statistics=simulated_statistics,
            timestamp=datetime.now(),
            is_simulated=True
        )
    
    def _simulate_tree_after_moves(
        self, 
        node: DirectoryNode, 
        files_to_move: set,
        dirs_to_remove: list
    ) -> DirectoryNode:
        """Recursively simulate tree structure after file moves.
        
        Args:
            node: Current node to process
            files_to_move: Set of file paths that would be moved
            dirs_to_remove: List of directories that would be removed
            
        Returns:
            New DirectoryNode with simulated structure
        """
        # Create a copy of the node
        simulated_node = DirectoryNode(
            path=node.path,
            name=node.name,
            is_directory=node.is_directory,
            size=node.size,
            category=node.category,
            depth=node.depth,
            is_new=node.is_new,
            is_removed=node.is_removed
        )
        
        # If it's a file, check if it would be moved
        if not node.is_directory:
            # Files that would be moved are not included in the simulated tree
            # (they'll be added to Scrubbed folder separately)
            return simulated_node
        
        # If it's a directory, process children
        simulated_children = []
        for child in node.children:
            # Skip files that would be moved
            if not child.is_directory and child.path in files_to_move:
                continue
            
            # Skip directories that would be removed
            if child.is_directory and child.path in dirs_to_remove:
                continue
            
            # Recursively simulate child
            simulated_child = self._simulate_tree_after_moves(
                child, 
                files_to_move,
                dirs_to_remove
            )
            simulated_children.append(simulated_child)
        
        simulated_node.children = simulated_children
        return simulated_node
    
    def _add_scrubbed_folder_to_tree(
        self, 
        root_node: DirectoryNode, 
        dry_run_stats: DryRunStats
    ) -> None:
        """Add Scrubbed folder structure to simulated tree.
        
        Args:
            root_node: Root node to add Scrubbed folder to
            dry_run_stats: DryRunStats with file operations
        """
        scrubbed_path = self.root_path / "Scrubbed"
        
        # Check if Scrubbed folder already exists in the tree
        scrubbed_node = None
        for child in root_node.children:
            if child.path == scrubbed_path:
                scrubbed_node = child
                break
        
        # If Scrubbed folder doesn't exist, create it
        if scrubbed_node is None:
            scrubbed_node = DirectoryNode(
                path=scrubbed_path,
                name="Scrubbed",
                is_directory=True,
                depth=root_node.depth + 1,
                is_new=True
            )
            root_node.children.append(scrubbed_node)
        
        # Group file operations by category
        by_category = {}
        for op in dry_run_stats.file_operations:
            category_name = op.category.value
            if category_name not in by_category:
                by_category[category_name] = []
            by_category[category_name].append(op)
        
        # Create category folders and add files
        for category_name, operations in by_category.items():
            category_path = scrubbed_path / category_name
            
            # Check if category folder already exists
            category_node = None
            for child in scrubbed_node.children:
                if child.path == category_path:
                    category_node = child
                    break
            
            # If category folder doesn't exist, create it
            if category_node is None:
                category_node = DirectoryNode(
                    path=category_path,
                    name=category_name,
                    is_directory=True,
                    depth=scrubbed_node.depth + 1,
                    is_new=True
                )
                scrubbed_node.children.append(category_node)
            
            # Add files to category folder
            for op in operations:
                # Use the destination filename (which may be resolved for conflicts)
                file_name = op.destination.name
                file_node = DirectoryNode(
                    path=op.destination,
                    name=file_name,
                    is_directory=False,
                    size=op.source.stat().st_size if op.source.exists() else 0,
                    category=op.category,
                    depth=category_node.depth + 1,
                    is_new=True
                )
                category_node.children.append(file_node)

    def render_before_tree(self, snapshot: DirectorySnapshot) -> None:
        """Display before tree with statistics.
        
        Args:
            snapshot: DirectorySnapshot to render
        """
        # Initialize console for rich output if available
        if RICH_AVAILABLE:
            console = Console()
        
        # Display "BEFORE" header with separator
        header = "\n" + "=" * 60
        title = "BEFORE: Current Directory Structure"
        footer = "=" * 60
        
        if RICH_AVAILABLE:
            console.print(header, style="bold yellow")
            console.print(title.center(60), style="bold yellow")
            console.print(footer, style="bold yellow")
        else:
            print(header)
            print(title.center(60))
            print(footer)
        
        # Render the tree
        self.renderer.render(snapshot, str(snapshot.root_path))
        
        # Display statistics
        self._display_statistics(snapshot)
        
        # Display separator after tree
        if RICH_AVAILABLE:
            console.print("\n" + "=" * 60, style="bold yellow")
        else:
            print("\n" + "=" * 60)
    
    def _display_statistics(self, snapshot: DirectorySnapshot) -> None:
        """Display statistics for a snapshot.
        
        Args:
            snapshot: DirectorySnapshot to display statistics for
        """
        # Initialize console for rich output if available
        if RICH_AVAILABLE:
            console = Console()
        
        stats = snapshot.statistics
        
        # Display statistics
        if RICH_AVAILABLE:
            console.print("\n📊 Statistics:", style="bold")
            console.print(f"  Files: {stats.total_files}")
            console.print(f"  Directories: {stats.total_directories}")
            console.print(f"  Total Size: {StatisticsCalculator.format_size(stats.total_size)}")
            console.print(f"  Max Depth: {stats.max_depth}")
        else:
            print("\nStatistics:")
            print(f"  Files: {stats.total_files}")
            print(f"  Directories: {stats.total_directories}")
            print(f"  Total Size: {StatisticsCalculator.format_size(stats.total_size)}")
            print(f"  Max Depth: {stats.max_depth}")
        
        # Display files by category if available
        if stats.files_by_category:
            if RICH_AVAILABLE:
                console.print("\n  Files by Category:", style="bold")
            else:
                print("\n  Files by Category:")
            
            for category, count in sorted(stats.files_by_category.items()):
                if RICH_AVAILABLE:
                    console.print(f"    {category}: {count}")
                else:
                    print(f"    {category}: {count}")

    def render_after_tree(self, snapshot: DirectorySnapshot, is_simulated: bool = False) -> None:
        """Display after tree with statistics and simulation indicator.
        
        Args:
            snapshot: DirectorySnapshot to render
            is_simulated: Whether this is a simulated after state
        """
        # Initialize console for rich output if available
        if RICH_AVAILABLE:
            console = Console()
        
        # Display "AFTER" header with simulation indicator if needed
        header = "\n" + "=" * 60
        if is_simulated:
            title = "AFTER: Simulated Directory Structure (DRY RUN)"
        else:
            title = "AFTER: Final Directory Structure"
        footer = "=" * 60
        
        if RICH_AVAILABLE:
            console.print(header, style="bold green")
            console.print(title.center(60), style="bold green")
            console.print(footer, style="bold green")
        else:
            print(header)
            print(title.center(60))
            print(footer)
        
        # Render the tree
        self.renderer.render(snapshot, str(snapshot.root_path))
        
        # Display statistics
        self._display_statistics(snapshot)
        
        # Display separator after tree
        if RICH_AVAILABLE:
            console.print("\n" + "=" * 60, style="bold green")
        else:
            print("\n" + "=" * 60)

    def display_comparison(self, before: DirectorySnapshot, after: DirectorySnapshot) -> None:
        """Display statistical comparison between states.
        
        Args:
            before: DirectorySnapshot from before state
            after: DirectorySnapshot from after state
        """
        TreeComparator.display_comparison(before, after)
