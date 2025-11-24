# Design Document

## Overview

The tree visualization feature adds a `--tree` flag to the `scrubb folder` command, providing users with before-and-after directory tree views and comprehensive statistics. This feature enhances the debugging and verification capabilities of the folder cleanup operation by making structural changes visible and quantifiable.

The design integrates seamlessly with the existing CLI architecture, reusing the `FolderOrganizer` and `FileClassifier` components while adding new modules for tree rendering and statistics collection. The feature supports both actual execution mode and dry-run mode, providing consistent visualization regardless of whether changes are applied.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│                      (cli.py: folder)                        │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├──> TreeVisualizer (new)
                │    ├─> DirectoryScanner
                │    ├─> TreeRenderer (rich library)
                │    └─> StatisticsCalculator
                │
                ├──> FolderOrganizer (existing)
                │    ├─> FileClassifier (existing)
                │    └─> DryRunFormatter (existing)
                │
                └──> TreeComparator (new)
                     └─> DeltaCalculator
```

### Component Interaction Flow

**Actual Execution Mode (`scrubb folder --tree`)**:
1. CLI parses `--tree` flag
2. TreeVisualizer captures "before" state
3. TreeVisualizer renders before tree and statistics
4. FolderOrganizer executes file operations
5. TreeVisualizer captures "after" state
6. TreeVisualizer renders after tree and statistics
7. TreeComparator calculates and displays deltas
8. Standard operation statistics displayed

**Dry-Run Mode (`scrubb folder --tree --dry`)**:
1. CLI parses `--tree` and `--dry` flags
2. TreeVisualizer captures "before" state
3. TreeVisualizer renders before tree and statistics
4. FolderOrganizer simulates operations (returns DryRunStats)
5. TreeVisualizer simulates "after" state from DryRunStats
6. TreeVisualizer renders simulated after tree with indicator
7. TreeComparator calculates and displays projected deltas
8. DryRunFormatter displays detailed operation preview

## Components and Interfaces

### 1. TreeVisualizer

**Purpose**: Main orchestrator for tree visualization functionality.

**Responsibilities**:
- Coordinate tree capture, rendering, and comparison
- Manage before/after state transitions
- Integrate with FolderOrganizer lifecycle

**Interface**:
```python
class TreeVisualizer:
    def __init__(self, root_path: Path, renderer: TreeRenderer):
        """Initialize with root directory and renderer."""
        
    def capture_before_state(self) -> DirectorySnapshot:
        """Capture current directory state before operations."""
        
    def capture_after_state(self) -> DirectorySnapshot:
        """Capture directory state after operations complete."""
        
    def simulate_after_state(self, dry_run_stats: DryRunStats) -> DirectorySnapshot:
        """Simulate after state based on dry-run operation plan."""
        
    def render_before_tree(self, snapshot: DirectorySnapshot) -> None:
        """Display before tree with statistics."""
        
    def render_after_tree(self, snapshot: DirectorySnapshot, is_simulated: bool = False) -> None:
        """Display after tree with statistics and simulation indicator."""
        
    def display_comparison(self, before: DirectorySnapshot, after: DirectorySnapshot) -> None:
        """Display statistical comparison between states."""
```

### 2. DirectoryScanner

**Purpose**: Scan and collect directory structure information.

**Responsibilities**:
- Traverse directory trees
- Collect file and folder metadata
- Calculate directory statistics

**Interface**:
```python
class DirectoryScanner:
    def __init__(self, classifier: FileClassifier):
        """Initialize with file classifier for categorization."""
        
    def scan(self, root_path: Path) -> DirectorySnapshot:
        """Scan directory and return snapshot with statistics."""
        
    def _traverse(self, path: Path, depth: int = 0) -> DirectoryNode:
        """Recursively traverse directory structure."""
        
    def _calculate_statistics(self, root_node: DirectoryNode) -> DirectoryStatistics:
        """Calculate comprehensive statistics from directory tree."""
```

### 3. TreeRenderer

**Purpose**: Render directory trees with professional formatting using the `rich` library.

**Responsibilities**:
- Generate visual tree representations
- Apply syntax highlighting and colors
- Handle terminal width constraints
- Format output with box-drawing characters

**Interface**:
```python
class TreeRenderer:
    def __init__(self, max_depth: int = None, max_files_per_dir: int = None):
        """Initialize renderer with display constraints."""
        
    def render(self, snapshot: DirectorySnapshot, title: str) -> None:
        """Render directory tree to console with title."""
        
    def _build_tree(self, node: DirectoryNode, tree: Tree, depth: int = 0) -> None:
        """Recursively build rich Tree structure."""
        
    def _format_file(self, file_path: Path, category: FileCategory) -> str:
        """Format file name with color based on category."""
        
    def _format_directory(self, dir_name: str, is_new: bool = False) -> str:
        """Format directory name with appropriate styling."""
```

### 4. StatisticsCalculator

**Purpose**: Calculate comprehensive directory statistics.

**Responsibilities**:
- Count files and directories
- Calculate total size
- Determine maximum depth
- Categorize files by type
- Calculate deltas between states

**Interface**:
```python
class StatisticsCalculator:
    @staticmethod
    def calculate(root_node: DirectoryNode, classifier: FileClassifier) -> DirectoryStatistics:
        """Calculate statistics from directory tree."""
        
    @staticmethod
    def calculate_delta(before: DirectoryStatistics, after: DirectoryStatistics) -> StatisticsDelta:
        """Calculate differences between two states."""
        
    @staticmethod
    def format_size(bytes: int) -> str:
        """Format byte size in human-readable format (KB, MB, GB)."""
```

### 5. TreeComparator

**Purpose**: Compare before and after states and display differences.

**Responsibilities**:
- Calculate statistical deltas
- Format comparison output
- Highlight significant changes

**Interface**:
```python
class TreeComparator:
    @staticmethod
    def display_comparison(before: DirectorySnapshot, after: DirectorySnapshot) -> None:
        """Display formatted comparison of before/after statistics."""
        
    @staticmethod
    def _format_delta(value: int, show_percentage: bool = False, base_value: int = None) -> str:
        """Format delta with +/- indicators and optional percentage."""
```

## Data Models

### DirectorySnapshot

Represents a complete snapshot of directory state at a point in time.

```python
@dataclass
class DirectorySnapshot:
    """Complete snapshot of directory state."""
    root_path: Path
    root_node: DirectoryNode
    statistics: DirectoryStatistics
    timestamp: datetime
    is_simulated: bool = False
```

### DirectoryNode

Represents a single node (file or directory) in the tree structure.

```python
@dataclass
class DirectoryNode:
    """Node in directory tree structure."""
    path: Path
    name: str
    is_directory: bool
    size: int = 0
    children: List[DirectoryNode] = field(default_factory=list)
    category: Optional[FileCategory] = None
    depth: int = 0
    is_new: bool = False  # For after-state visualization
    is_removed: bool = False  # For comparison purposes
```

### DirectoryStatistics

Comprehensive statistics about a directory structure.

```python
@dataclass
class DirectoryStatistics:
    """Statistics for directory structure."""
    total_files: int = 0
    total_directories: int = 0
    total_size: int = 0
    max_depth: int = 0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    size_by_category: Dict[str, int] = field(default_factory=dict)
```

### StatisticsDelta

Represents changes between two directory states.

```python
@dataclass
class StatisticsDelta:
    """Delta between two directory states."""
    files_delta: int
    directories_delta: int
    size_delta: int
    depth_delta: int
    category_deltas: Dict[str, int] = field(default_factory=dict)
    
    def format_delta_value(self, value: int) -> str:
        """Format delta with +/- prefix and color."""
        if value > 0:
            return f"[green]+{value}[/green]"
        elif value < 0:
            return f"[red]{value}[/red]"
        else:
            return f"[dim]{value}[/dim]"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Tree capture consistency

*For any* directory state, capturing a snapshot and immediately capturing another snapshot without intervening operations should produce equivalent statistics.
**Validates: Requirements 1.3, 1.4**

### Property 2: Statistics calculation correctness

*For any* directory tree, the sum of files in all categories should equal the total file count in the statistics.
**Validates: Requirements 2.1, 2.5**

### Property 3: Delta calculation symmetry

*For any* two directory snapshots A and B, the delta from A to B should be the negation of the delta from B to A.
**Validates: Requirements 6.2, 6.3, 6.4, 6.5**

### Property 4: Dry-run simulation accuracy

*For any* dry-run operation, the simulated after-state file count should equal the before-state file count (files are moved, not created or deleted).
**Validates: Requirements 7.2, 7.3**

### Property 5: Tree rendering idempotence

*For any* directory snapshot, rendering it multiple times should produce identical output.
**Validates: Requirements 3.2, 3.3, 9.3**

### Property 6: Category file count consistency

*For any* directory snapshot, the sum of files in the Scrubbed folder's category subdirectories should equal the total files moved count from operation statistics.
**Validates: Requirements 11.3, 11.4**

### Property 7: Directory count accuracy

*For any* directory tree, the total directory count should equal the number of nodes where is_directory is True.
**Validates: Requirements 2.2**

### Property 8: Depth calculation correctness

*For any* directory tree, the maximum depth should be greater than or equal to the depth of any individual node in the tree.
**Validates: Requirements 2.3**

### Property 9: Size calculation consistency

*For any* directory tree, the total size should equal the sum of all file sizes in the tree.
**Validates: Requirements 2.4**

### Property 10: Before-after file conservation

*For any* actual execution (non-dry-run), the number of files in the before state should equal the number of files in the after state (files are moved, not created or deleted).
**Validates: Requirements 1.3, 1.4, 5.3**

## Error Handling

### Tree Rendering Failures

**Strategy**: Graceful degradation with fallback to simple text output.

- If `rich` library is unavailable, fall back to basic text tree using ASCII characters
- If rendering fails mid-operation, log error and continue with cleanup
- Display partial tree if complete rendering fails

**Implementation**:
```python
try:
    from rich.tree import Tree
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Use fallback SimpleTreeRenderer
```

### Permission Errors

**Strategy**: Mark inaccessible directories and continue.

- Catch `PermissionError` during directory traversal
- Add marker to tree indicating restricted access
- Include count of inaccessible directories in statistics
- Continue scanning accessible portions

### Statistics Calculation Errors

**Strategy**: Provide partial statistics with error indicators.

- If size calculation fails for a file, use 0 and increment error count
- If category classification fails, mark as "Unknown"
- Display warning about incomplete statistics
- Continue with available data

### Simulation Errors

**Strategy**: Fall back to before-state only display.

- If after-state simulation fails in dry-run mode, display error message
- Show only before-state tree and statistics
- Provide standard dry-run output from DryRunFormatter
- Log detailed error for debugging

## Testing Strategy

### Unit Testing

**Test Coverage**:
- DirectoryScanner: Test scanning various directory structures (empty, nested, large)
- StatisticsCalculator: Test calculation accuracy with known directory structures
- TreeComparator: Test delta calculations with various before/after scenarios
- TreeRenderer: Test formatting and truncation logic
- Error handling: Test graceful degradation for each error scenario

**Example Unit Tests**:
```python
def test_scanner_empty_directory():
    """Test scanning an empty directory returns correct statistics."""
    
def test_statistics_category_sum():
    """Test that category file counts sum to total file count."""
    
def test_delta_calculation_symmetry():
    """Test that delta(A, B) = -delta(B, A)."""
    
def test_renderer_fallback():
    """Test fallback to simple renderer when rich is unavailable."""
```

### Property-Based Testing

**Property Tests**:
- Test that statistics remain consistent across multiple scans of the same directory
- Test that delta calculations are symmetric
- Test that file counts are conserved in before/after states
- Test that tree rendering is idempotent
- Test that category sums equal total counts

**Testing Framework**: Use `hypothesis` library (already in project dependencies based on `.hypothesis` directory).

**Example Property Test**:
```python
from hypothesis import given, strategies as st

@given(st.lists(st.text(), min_size=0, max_size=100))
def test_file_count_conservation(file_names):
    """Property: File count should be conserved in before/after states."""
    # Create temporary directory with files
    # Capture before state
    # Execute organization
    # Capture after state
    # Assert before.total_files == after.total_files
```

### Integration Testing

**Test Scenarios**:
- Test `--tree` flag with actual execution on sample directory
- Test `--tree --dry` flags together on sample directory
- Test tree visualization with various directory sizes (small, medium, large)
- Test integration with existing FolderOrganizer and DryRunFormatter output
- Test terminal width handling with different console sizes

## Implementation Notes

### Third-Party Library Selection

**Chosen Library**: `rich` (https://github.com/Textualize/rich)

**Rationale**:
- Professional tree rendering with box-drawing characters
- Built-in syntax highlighting and color support
- Excellent terminal width handling
- Active maintenance and wide adoption
- No emoji dependencies (meets requirement 3.5)
- Supports fallback for environments without color support

**Installation**: Add to `pyproject.toml` dependencies:
```toml
dependencies = [
    "typer>=0.12.3",
    "rich>=13.0.0"
]
```

### CLI Integration

**Modified `folder` Command**:
```python
@app.command()
def folder(
    dry: bool = typer.Option(False, "--dry", help="Preview changes without executing them"),
    tree: bool = typer.Option(False, "--tree", help="Display directory tree before and after execution")
):
    """Organize files into categorized folders and remove empty directories."""
    
    # Display dry-run mode header if enabled
    if dry:
        typer.secho("\n🔍 DRY RUN MODE - No changes will be made\n", fg=typer.colors.YELLOW, bold=True)
    
    # Prompt for directory path
    path_input = typer.prompt("Enter the directory path to organize")
    path_input = path_input.strip().strip('"').strip("'")
    target_path = Path(path_input).expanduser().resolve()
    
    # Validate path
    if not target_path.exists():
        typer.secho(f"Error: Path does not exist: {target_path}", fg="red", err=True)
        raise typer.Exit(code=1)
    
    if not target_path.is_dir():
        typer.secho(f"Error: Path is not a directory: {target_path}", fg="red", err=True)
        raise typer.Exit(code=1)
    
    # Initialize components
    classifier = FileClassifier()
    organizer = FolderOrganizer(target_path, classifier, dry_run=dry)
    
    # Tree visualization if enabled
    if tree:
        visualizer = TreeVisualizer(target_path, TreeRenderer())
        before_snapshot = visualizer.capture_before_state()
        visualizer.render_before_tree(before_snapshot)
    
    # Execute organization
    typer.echo(f"Organizing files in: {target_path}")
    stats = organizer.organize()
    
    # Tree visualization after execution
    if tree:
        if dry:
            after_snapshot = visualizer.simulate_after_state(stats)
            visualizer.render_after_tree(after_snapshot, is_simulated=True)
        else:
            after_snapshot = visualizer.capture_after_state()
            visualizer.render_after_tree(after_snapshot, is_simulated=False)
        
        visualizer.display_comparison(before_snapshot, after_snapshot)
    
    # Display standard statistics
    if dry:
        formatted_output = DryRunFormatter.format_output(stats, target_path)
        typer.echo(formatted_output)
    else:
        # ... existing actual mode output ...
```

### Performance Considerations

**Large Directory Handling**:
- Implement depth limiting (default: no limit, configurable)
- Implement file count limiting per directory (default: show all, configurable)
- Use lazy evaluation for tree building where possible
- Cache statistics calculations to avoid redundant traversals

**Memory Management**:
- Stream large directory listings rather than loading all into memory
- Use generators for directory traversal
- Clear snapshots after rendering to free memory

### Backward Compatibility

- The `--tree` flag is optional; existing behavior unchanged when not provided
- No changes to existing command signatures or output formats
- Tree visualization output is additive, not replacing existing output
- Graceful fallback ensures functionality even if `rich` library unavailable
