# Design Document: Architectural Unification and Professional Code Standards

## Overview

This design document specifies a comprehensive architectural refactoring that eliminates all technical debt identified in the codebase audit. This is NOT incremental improvement - this is a complete rewrite of core modules following professional software engineering principles.

### Core Principles

1. **Separation of Concerns** - Clear boundaries between CLI, business logic, and I/O
2. **Dependency Injection** - All dependencies injected, enabling testing and flexibility
3. **Fail Fast** - Invalid data causes immediate exceptions, not silent failures
4. **Single Responsibility** - Each class has one reason to change
5. **Open/Closed** - Open for extension, closed for modification
6. **Interface Segregation** - Clients depend only on interfaces they use
7. **Dependency Inversion** - Depend on abstractions, not concretions

### What Gets Rewritten

**Complete Rewrites:**
- `scrubb/cli.py` - Extract business logic, eliminate duplication
- `scrubb/folder_organizer.py` - Fix O(n²) algorithms, separate concerns
- `scrubb/tree_visualizer.py` - Fix broken simulation logic
- `scrubb/directory_scanner.py` - Add proper error tracking
- `scrubb/statistics_calculator.py` - Remove theatrical error handling
- `scrubb/scrubber.py` - Fix emoji regex, use grapheme clusters

**New Modules:**
- `scrubb/core/interfaces.py` - Define all interfaces
- `scrubb/core/result.py` - Result types for operations
- `scrubb/core/validation.py` - Input validation
- `scrubb/core/errors.py` - Exception hierarchy
- `scrubb/io/file_operations.py` - File I/O abstraction
- `scrubb/io/directory_operations.py` - Directory I/O abstraction
- `scrubb/business/organizer.py` - Pure business logic
- `scrubb/business/classifier.py` - Enhanced classifier
- `scrubb/business/conflict_resolver.py` - Conflict resolution
- `scrubb/cli/commands.py` - CLI command handlers
- `scrubb/cli/output.py` - Output formatting
- `scrubb/cli/input.py` - Input handling and validation

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Layer                           │
│  - Command handlers                                     │
│  - Input validation                                     │
│  - Output formatting                                    │
│  - User interaction                                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                   │
│  - File organization                                    │
│  - File classification                                  │
│  - Conflict resolution                                  │
│  - Tree simulation                                      │
│  - Statistics calculation                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      I/O Layer                          │
│  - File operations                                      │
│  - Directory operations                                 │
│  - Path resolution                                      │
│  - Permission handling                                  │
└─────────────────────────────────────────────────────────┘
```

### Module Structure

```
scrubb/
├── core/
│   ├── __init__.py
│   ├── interfaces.py      # All interface definitions
│   ├── result.py          # Result types
│   ├── validation.py      # Input validation
│   ├── errors.py          # Exception hierarchy
│   └── constants.py       # Named constants
├── io/
│   ├── __init__.py
│   ├── file_operations.py # File I/O abstraction
│   ├── directory_operations.py # Directory I/O
│   └── path_validator.py  # Path validation and security
├── business/
│   ├── __init__.py
│   ├── organizer.py       # File organization logic
│   ├── classifier.py      # File classification
│   ├── conflict_resolver.py # Name conflict resolution
│   ├── tree_builder.py    # Tree structure building
│   ├── statistics.py      # Statistics calculation
│   └── emoji_detector.py  # Emoji detection and removal
├── cli/
│   ├── __init__.py
│   ├── commands.py        # Command handlers
│   ├── output.py          # Output formatting
│   ├── input.py           # Input handling
│   └── app.py             # Typer app configuration
└── legacy/
    └── ... (old modules for backward compatibility)
```

## Components and Interfaces

### Core Interfaces

```python
# scrubb/core/interfaces.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Protocol
from .result import Result, OperationResult
from .errors import ValidationError

class FileOperations(Protocol):
    """Interface for file I/O operations."""
    
    def read_file(self, path: Path) -> Result[str]:
        """Read file content."""
        ...
    
    def write_file(self, path: Path, content: str) -> Result[None]:
        """Write content to file."""
        ...
    
    def move_file(self, source: Path, destination: Path) -> Result[None]:
        """Move file from source to destination."""
        ...
    
    def delete_file(self, path: Path) -> Result[None]:
        """Delete file."""
        ...
    
    def file_exists(self, path: Path) -> bool:
        """Check if file exists."""
        ...
    
    def get_file_size(self, path: Path) -> Result[int]:
        """Get file size in bytes."""
        ...


class DirectoryOperations(Protocol):
    """Interface for directory I/O operations."""
    
    def create_directory(self, path: Path) -> Result[None]:
        """Create directory."""
        ...
    
    def remove_directory(self, path: Path) -> Result[None]:
        """Remove empty directory."""
        ...
    
    def list_directory(self, path: Path) -> Result[List[Path]]:
        """List directory contents."""
        ...
    
    def is_empty(self, path: Path) -> Result[bool]:
        """Check if directory is empty."""
        ...
    
    def directory_exists(self, path: Path) -> bool:
        """Check if directory exists."""
        ...


class FileClassifier(Protocol):
    """Interface for file classification."""
    
    def classify(self, path: Path) -> FileCategory:
        """Classify file by extension."""
        ...
    
    def get_category_name(self, category: FileCategory) -> str:
        """Get display name for category."""
        ...


class ConflictResolver(Protocol):
    """Interface for name conflict resolution."""
    
    def resolve(self, path: Path, existing: set[Path]) -> Path:
        """Resolve name conflict by generating unique name."""
        ...


class TreeRenderer(Protocol):
    """Interface for tree rendering."""
    
    def render(self, snapshot: DirectorySnapshot, title: str) -> str:
        """Render directory tree to string."""
        ...


class PathValidator(Protocol):
    """Interface for path validation."""
    
    def validate(self, path: Path, root: Path) -> Result[Path]:
        """Validate path is within root and safe."""
        ...
    
    def resolve(self, path: str, root: Path) -> Result[Path]:
        """Resolve and validate user-provided path."""
        ...
```

### Result Types

```python
# scrubb/core/result.py

from dataclasses import dataclass
from typing import Generic, TypeVar, Union
from .errors import ScrubbError

T = TypeVar('T')

@dataclass(frozen=True)
class Success(Generic[T]):
    """Successful operation result."""
    value: T
    
    def is_success(self) -> bool:
        return True
    
    def is_failure(self) -> bool:
        return False
    
    def unwrap(self) -> T:
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        return self.value


@dataclass(frozen=True)
class Failure(Generic[T]):
    """Failed operation result."""
    error: ScrubbError
    
    def is_success(self) -> bool:
        return False
    
    def is_failure(self) -> bool:
        return True
    
    def unwrap(self) -> T:
        raise self.error
    
    def unwrap_or(self, default: T) -> T:
        return default


Result = Union[Success[T], Failure[T]]


@dataclass
class OperationResult:
    """Result of a file organization operation."""
    files_moved: int
    files_by_category: Dict[str, int]
    empty_folders_removed: int
    critical_errors: List[ScrubbError]
    warnings: List[ScrubbError]
    
    @property
    def success(self) -> bool:
        """Operation succeeded if no critical errors."""
        return len(self.critical_errors) == 0
    
    @property
    def total_errors(self) -> int:
        """Total number of errors (critical + warnings)."""
        return len(self.critical_errors) + len(self.warnings)
```

### Error Hierarchy

```python
# scrubb/core/errors.py

class ScrubbError(Exception):
    """Base exception for all scrubb errors."""
    
    def __init__(self, message: str, context: dict[str, any] | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class ValidationError(ScrubbError):
    """Input validation failed."""
    pass


class ConfigurationError(ScrubbError):
    """Configuration is invalid."""
    pass


class FileOperationError(ScrubbError):
    """File operation failed."""
    pass


class DirectoryOperationError(ScrubbError):
    """Directory operation failed."""
    pass


class PathSecurityError(ScrubbError):
    """Path validation failed for security reasons."""
    pass


class ClassificationError(ScrubbError):
    """File classification failed."""
    pass
```

### Constants

```python
# scrubb/core/constants.py

from enum import Enum

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INVALID_INPUT = 2
EXIT_USER_CANCELLED = 130

# File size units
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

# Default limits
MAX_FILES_PER_DIR_DISPLAY = 100
MAX_TREE_DEPTH_DISPLAY = 10
MAX_ERRORS_TO_DISPLAY = 10

# Configuration keys
CONFIG_KEY_DEFAULT_ROOT = "default_root"
CONFIG_KEY_IGNORE_PATTERNS = "ignore_patterns"
CONFIG_KEY_TEXT_EXTENSIONS = "text_extensions"

class OperationStatus(Enum):
    """Status of an operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorSeverity(Enum):
    """Severity level of an error."""
    CRITICAL = "critical"  # Prevents primary function
    WARNING = "warning"    # Doesn't prevent primary function
    INFO = "info"          # Informational only
```

## Data Models

### Enhanced File Classification

```python
# scrubb/business/classifier.py

from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class FileCategory(Enum):
    """Categories for file organization."""
    IMAGE = "Images"
    VIDEO = "Video"
    MARKDOWN = "Docs/Markdown"
    DOCUMENT = "Docs/Other Docs"
    DEVELOPMENT = "Development"
    OTHER = "Other"


@dataclass(frozen=True)
class ClassificationRule:
    """Rule for classifying files."""
    extensions: frozenset[str]
    category: FileCategory
    priority: int = 0  # Higher priority rules checked first


class EnhancedFileClassifier:
    """Enhanced file classifier with configurable rules."""
    
    def __init__(self, rules: list[ClassificationRule] | None = None):
        self.rules = rules or self._default_rules()
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def classify(self, path: Path) -> FileCategory:
        """Classify file by extension."""
        extension = path.suffix.lower()
        
        if not extension:
            return FileCategory.OTHER
        
        for rule in self.rules:
            if extension in rule.extensions:
                return rule.category
        
        return FileCategory.OTHER
    
    @staticmethod
    def _default_rules() -> list[ClassificationRule]:
        """Default classification rules."""
        return [
            ClassificationRule(
                extensions=frozenset({
                    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
                    ".svg", ".webp", ".ico", ".tiff", ".tif"
                }),
                category=FileCategory.IMAGE,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({
                    ".mp4", ".avi", ".mov", ".mkv", ".flv",
                    ".wmv", ".webm", ".m4v", ".mpeg", ".mpg"
                }),
                category=FileCategory.VIDEO,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({".md", ".markdown"}),
                category=FileCategory.MARKDOWN,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({
                    ".pdf", ".doc", ".docx", ".txt", ".rtf",
                    ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"
                }),
                category=FileCategory.DOCUMENT,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({
                    ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
                    ".c", ".cpp", ".h", ".hpp", ".rs", ".go",
                    ".rb", ".php", ".html", ".css", ".scss",
                    ".json", ".xml", ".yaml", ".yml", ".toml",
                    ".sh", ".bash", ".sql", ".r", ".swift", ".kt"
                }),
                category=FileCategory.DEVELOPMENT,
                priority=10
            ),
        ]
```

### Efficient Directory Operations

```python
# scrubb/business/organizer.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from ..core.result import Result, Success, Failure, OperationResult
from ..core.errors import FileOperationError, DirectoryOperationError
from ..core.interfaces import FileOperations, DirectoryOperations, FileClassifier, ConflictResolver

@dataclass
class OrganizationPlan:
    """Plan for organizing files."""
    files_to_move: list[tuple[Path, Path]]  # (source, destination)
    directories_to_create: set[Path]
    directories_to_remove: list[Path]  # Ordered bottom-up
    conflicts: dict[Path, Path]  # original -> resolved


class FileOrganizer:
    """Pure business logic for file organization."""
    
    def __init__(
        self,
        file_ops: FileOperations,
        dir_ops: DirectoryOperations,
        classifier: FileClassifier,
        conflict_resolver: ConflictResolver,
    ):
        self.file_ops = file_ops
        self.dir_ops = dir_ops
        self.classifier = classifier
        self.conflict_resolver = conflict_resolver
    
    def plan_organization(
        self,
        root: Path,
        scrubbed_folder: Path,
    ) -> Result[OrganizationPlan]:
        """
        Plan file organization without making changes.
        
        This is O(n) where n is the number of files.
        """
        plan = OrganizationPlan(
            files_to_move=[],
            directories_to_create=set(),
            directories_to_remove=[],
            conflicts={},
        )
        
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
                    
                    # Track for conflict resolution
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
        """
        Execute organization plan.
        
        This is O(n) where n is the number of operations.
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
        """Check if path is within scrubbed folder."""
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
        """Check if directory will be empty after moves."""
        # If directory has files that won't be moved, it won't be empty
        if dir_path in files_by_dir and files_by_dir[dir_path]:
            return False
        
        # Check if any subdirectories won't be empty
        for subdir in files_by_dir:
            if subdir != dir_path and subdir.is_relative_to(dir_path):
                if not self._will_be_empty(subdir, files_by_dir):
                    return False
        
        return True
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Code Duplication Elimination
*For any* two functions in the codebase, if they perform the same operation, they should call a shared implementation
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

### Property 2: Layer Separation
*For any* CLI function, it should not directly access file system operations; it should call business logic
**Validates: Requirements 2.1, 2.2, 2.3**

### Property 3: Algorithm Efficiency
*For any* directory with n files, empty directory detection should complete in O(n) time, not O(n²)
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Error Propagation
*For any* invalid input, the system should raise an exception immediately, not return partial results
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 5: Type Consistency
*For any* function with type hints, mypy should report zero type errors
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 6: Simulation Accuracy
*For any* dry-run operation, the simulated after-state should match what would result from actual execution
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

### Property 7: Path Security
*For any* user-provided path, if it contains `..` or attempts to escape the root, validation should fail
**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

### Property 8: Emoji Detection Completeness
*For any* Unicode emoji, the emoji regex should match it
**Validates: Requirements 8.1, 8.2, 8.3**

### Property 9: Exception Specificity
*For any* caught exception, it should be a specific exception type, not a bare except clause
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 10: Dependency Injection
*For any* component with dependencies, those dependencies should be injected via constructor
**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

## Error Handling

### Error Classification

1. **CRITICAL** - Prevents primary function (file organization)
   - File move failures
   - Invalid paths
   - Permission errors on files

2. **WARNING** - Doesn't prevent primary function
   - Directory removal failures
   - Permission errors on directories
   - OneDrive/cloud storage issues

3. **INFO** - Informational only
   - Files already organized
   - No files to process

### Error Recovery Strategy

- **CRITICAL**: Log error, continue with next file, report at end
- **WARNING**: Log warning, continue operation
- **INFO**: Log info, continue operation

### Error Context

All errors include:
- Error message
- Context dictionary with relevant details
- Stack trace (in debug mode)

## Testing Strategy

### Unit Testing

- Test each component in isolation
- Mock all dependencies
- Test success and failure paths
- Test edge cases

### Property-Based Testing

Use Hypothesis with minimum 100 iterations:

**Property Test 1: Code Duplication**
- **Feature**: architectural-unification, Property 1
- Verify no duplicate code patterns

**Property Test 2: Layer Separation**
- **Feature**: architectural-unification, Property 2
- Verify CLI doesn't access I/O directly

**Property Test 3: Algorithm Efficiency**
- **Feature**: architectural-unification, Property 3
- Verify O(n) complexity for directory operations

**Property Test 4: Error Propagation**
- **Feature**: architectural-unification, Property 4
- Verify invalid input raises exceptions

**Property Test 5: Type Consistency**
- **Feature**: architectural-unification, Property 5
- Verify mypy reports zero errors

**Property Test 6: Simulation Accuracy**
- **Feature**: architectural-unification, Property 6
- Verify dry-run matches actual execution

**Property Test 7: Path Security**
- **Feature**: architectural-unification, Property 7
- Verify path validation prevents traversal

**Property Test 8: Emoji Detection**
- **Feature**: architectural-unification, Property 8
- Verify all emojis are detected

**Property Test 9: Exception Specificity**
- **Feature**: architectural-unification, Property 9
- Verify no bare except clauses

**Property Test 10: Dependency Injection**
- **Feature**: architectural-unification, Property 10
- Verify all dependencies are injected

### Integration Testing

- Test complete workflows end-to-end
- Use real file systems (temporary directories)
- Verify all components work together
- Test error scenarios

### Performance Benchmarking

- Benchmark critical operations
- Measure time for various input sizes
- Verify O(n) complexity empirically
- Fail CI if performance regresses

## Migration Strategy

### Phase 1: Create New Architecture (Week 1)
1. Create new module structure
2. Implement core interfaces
3. Implement result types
4. Implement error hierarchy
5. Implement constants

### Phase 2: Implement I/O Layer (Week 1)
1. Implement FileOperations
2. Implement DirectoryOperations
3. Implement PathValidator
4. Add comprehensive tests

### Phase 3: Implement Business Logic (Week 2)
1. Implement EnhancedFileClassifier
2. Implement ConflictResolver
3. Implement FileOrganizer
4. Implement TreeBuilder
5. Add comprehensive tests

### Phase 4: Implement CLI Layer (Week 2)
1. Implement command handlers
2. Implement output formatting
3. Implement input handling
4. Add comprehensive tests

### Phase 5: Integration and Testing (Week 3)
1. Integration tests
2. Property-based tests
3. Performance benchmarks
4. Documentation

### Phase 6: Migration and Cleanup (Week 3)
1. Update existing code to use new architecture
2. Remove deprecated code
3. Update documentation
4. Final testing

### Phase 7: Release (Week 4)
1. Version bump (2.0.0 - breaking changes)
2. Update CHANGELOG
3. Release notes
4. Deploy

## Performance Considerations

### Algorithmic Improvements

- **Before**: O(n²) empty directory detection
- **After**: O(n) with single-pass traversal

- **Before**: Multiple tree traversals
- **After**: Single traversal collecting all data

- **Before**: Repeated file system calls
- **After**: Batch operations where possible

### Memory Optimization

- Use generators for large directory trees
- Stream file content for large files
- Limit in-memory data structures

## Security Considerations

### Path Validation

- Validate all user-provided paths
- Prevent directory traversal attacks
- Check for null bytes and special characters
- Validate symlink targets

### Permission Handling

- Check permissions before operations
- Handle permission errors gracefully
- Don't expose sensitive paths in errors

## Future Extensions

- Plugin system for custom classifiers
- Configuration profiles
- Undo/redo functionality
- Parallel file operations
- Cloud storage integration
