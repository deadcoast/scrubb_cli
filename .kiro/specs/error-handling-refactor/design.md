# Design Document: Error Handling Architecture Refactor

## Overview

This design refactors the error handling system to fix a broken, half-migrated codebase. The current code has:
- Broken references to non-existent attributes (`self.file_stats`, `self.directory_stats`)
- Imports from non-existent modules (`operation_results.py` was created but never properly integrated)
- Multiple conflicting result tracking systems
- Directory cleanup failures counted as critical errors

This refactor will:
1. **Remove all broken code** - Delete half-implemented features
2. **Use ONLY OrganizationStats** - Single source of truth
3. **Separate error types** - Add `critical_errors` and `warnings` lists to OrganizationStats
4. **Fix the UX** - Directory permission errors are warnings, not failures

## Architecture

### Current Problems

1. **Broken Code**: References to `self.file_stats`, `self.directory_stats`, `self.critical_errors`, `self.warnings` that don't exist
2. **Non-existent Imports**: Code imports `OperationError`, `OperationType`, etc. from modules that don't exist
3. **Conflated Errors**: Directory permission errors counted as critical errors in `stats.errors`
4. **Half-Migrated**: Previous agent added `operation_results.py` but never integrated it properly

### Proposed Architecture (SIMPLE)

```

                      FolderOrganizer                        
  - Uses ONLY OrganizationStats                              
  - Tracks critical_errors list (file move failures)         
  - Tracks warnings list (directory cleanup issues)          
  - Returns OrganizationStats                                


@dataclass
class OrganizationStats:
    files_moved: int
    files_by_category: Dict[str, int]
    empty_folders_removed: int
    critical_errors: List[str]  # NEW: File move failures
    warnings: List[str]          # NEW: Directory cleanup issues
    
    @property
    def success(self) -> bool:
        return len(self.critical_errors) == 0
```

**Key Principle**: Keep it simple. One stats object. Two error lists. That's it.

## Components and Interfaces

### 1. OrganizationStats (scrubb/folder_organizer.py)

**ONLY change to existing dataclass**:

```python
@dataclass
class OrganizationStats:
    """Statistics for folder organization operations."""
    files_moved: int = 0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    empty_folders_removed: int = 0
    critical_errors: List[str] = field(default_factory=list)  # NEW
    warnings: List[str] = field(default_factory=list)         # NEW
    
    # REMOVE these old fields:
    # errors: int = 0  # DELETE
    # error_files: List[str] = field(default_factory=list)  # DELETE
    # directory_permission_warnings: int = 0  # DELETE
    
    @property
    def success(self) -> bool:
        """Operation succeeded if no critical errors"""
        return len(self.critical_errors) == 0
```

That's it. No new modules. No new classes. Just fix the existing one.

### 2. FolderOrganizer Refactor

**Key Changes:**
- Remove ALL broken references (`self.file_stats`, `self.directory_stats`, `self.critical_errors`, `self.warnings`)
- Remove ALL imports from non-existent modules
- Use ONLY `self.stats` (OrganizationStats)
- Add errors to `stats.critical_errors` or `stats.warnings` lists

```python
class FolderOrganizer:
    def __init__(self, root_path: Path, classifier: FileClassifier, dry_run: bool = False):
        self.root_path = root_path.resolve()
        self.scrubbed_path = self.root_path / "Scrubbed"
        self.classifier = classifier
        self.dry_run = dry_run
        self.stats = OrganizationStats()  # ONLY stats object
    
    def _move_file(self, file_path: Path, category: FileCategory) -> bool:
        """Move a file to its category folder."""
        try:
            category_dir = self.scrubbed_path / category.value
            category_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = category_dir / file_path.name
            if dest_path.exists():
                dest_path = self._handle_name_conflict(dest_path)
            
            shutil.move(str(file_path), str(dest_path))
            
            # Update stats
            self.stats.files_moved += 1
            category_name = category.value
            self.stats.files_by_category[category_name] = \
                self.stats.files_by_category.get(category_name, 0) + 1
            
            return True
            
        except PermissionError:
            # CRITICAL: File move failed
            self.stats.critical_errors.append(
                f"Permission denied moving file: {file_path}"
            )
            return False
        except OSError as e:
            # CRITICAL: File move failed
            self.stats.critical_errors.append(
                f"Failed to move {file_path}: {str(e)}"
            )
            return False
    
    def _remove_empty_folders(self) -> int:
        """Remove all empty directories, return count removed."""
        removed_count = 0
        
        for dirpath, dirnames, filenames in sorted(
            self.root_path.walk(top_down=False), 
            key=lambda x: str(x[0]), 
            reverse=True
        ):
            dir_path = Path(dirpath)
            
            if dir_path == self.root_path:
                continue
            
            try:
                dir_path.relative_to(self.scrubbed_path)
                continue
            except ValueError:
                pass
            
            if self._is_empty_directory(dir_path):
                try:
                    # Remove ignored files first
                    for item in dir_path.iterdir():
                        if item.is_file() and item.name in self.IGNORED_FILES:
                            try:
                                item.unlink()
                            except (PermissionError, OSError):
                                pass
                    
                    dir_path.rmdir()
                    removed_count += 1
                    
                except PermissionError:
                    # WARNING: Directory cleanup failed (not critical)
                    self.stats.warnings.append(
                        f"Permission denied removing directory: {dir_path}"
                    )
                except OSError as e:
                    # WARNING: Directory cleanup failed (not critical)
                    self.stats.warnings.append(
                        f"Failed to remove directory {dir_path}: {str(e)}"
                    )
        
        return removed_count
```

### 3. CLI Integration

**Key Changes:**
- Use `OrganizationStats` (no new types)
- Check `stats.success` property
- Display critical errors prominently
- Display warnings separately (only in verbose mode)

```python
def folder(...):
    # ... existing code ...
    
    stats = organizer.organize()
    
    # Header
    typer.echo("\n" + "=" * 50)
    if stats.success:
        typer.secho("Folder cleanup complete!", fg="green", bold=True)
    else:
        typer.secho("Folder organization failed", fg="red", bold=True)
    typer.echo("=" * 50 + "\n")
    
    # Stats
    typer.echo(f"Files moved: {stats.files_moved}")
    
    if stats.files_by_category:
        typer.echo("\nFiles moved by category:")
        for category, count in sorted(stats.files_by_category.items()):
            typer.echo(f"  {category}: {count}")
    
    typer.echo(f"\nEmpty folders removed: {stats.empty_folders_removed}")
    
    # Critical errors (always shown)
    if stats.critical_errors:
        typer.secho(f"\nErrors encountered: {len(stats.critical_errors)}", fg="red")
        for error in stats.critical_errors[:10]:  # Show first 10
            typer.echo(f"  [X] {error}")
        if len(stats.critical_errors) > 10:
            typer.echo(f"  ... and {len(stats.critical_errors) - 10} more errors")
    
    # Warnings (only in verbose mode)
    if stats.warnings and verbosity_manager.should_print_debug():
        typer.secho(f"\nWarnings: {len(stats.warnings)}", fg="yellow")
        typer.echo("(These don't indicate failure)")
        for warning in stats.warnings[:5]:  # Show first 5
            typer.echo(f"  [!] {warning}")
```

## Data Models

Only ONE dataclass changes:

```python
@dataclass
class OrganizationStats:
    files_moved: int = 0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    empty_folders_removed: int = 0
    critical_errors: List[str] = field(default_factory=list)  # NEW
    warnings: List[str] = field(default_factory=list)         # NEW
    
    @property
    def success(self) -> bool:
        return len(self.critical_errors) == 0
```

That's it. No new modules. No new classes.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Error Classification Consistency
*For any* operation error, if it prevents file moves, it should be classified as CRITICAL; if it only affects directory cleanup, it should be classified as WARNING
**Validates: Requirements 2.1, 2.2**

### Property 2: Success Determination
*For any* operation summary, the overall success should be true if and only if there are no critical errors in file operations
**Validates: Requirements 2.4**

### Property 3: Result Completeness
*For any* folder organization operation, the returned OperationSummary should account for all files discovered and all directories processed
**Validates: Requirements 1.3**

### Property 4: Error Message Structure
*For any* operation error with severity CRITICAL, it should include both a message and a suggestion for resolution
**Validates: Requirements 2.5**

### Property 5: Separation of Concerns
*For any* operation summary, file operation errors should not appear in directory cleanup warnings, and vice versa
**Validates: Requirements 4.2, 4.3, 4.4**

## Error Handling

### Error Classification Rules

1. **CRITICAL Errors** (prevent primary function):
   - File move failures (PermissionError, OSError)
   - File read failures
   - Invalid paths
   - Disk full errors

2. **WARNING** (don't prevent primary function):
   - Directory removal failures
   - Permission errors on empty directories
   - OneDrive/cloud storage protection

3. **INFO** (informational only):
   - Skipped files (already in correct location)
   - No files to organize

### Error Recovery

- **CRITICAL**: Stop processing current file, continue with next file
- **WARNING**: Log warning, continue operation
- **INFO**: Log info, continue operation

## Testing Strategy

### Unit Tests

- Test error classification logic
- Test result aggregation
- Test success determination
- Test error message formatting

### Property-Based Tests

We'll use Hypothesis for property-based testing with a minimum of 100 iterations per test.

**Property Test 1: Error Classification Consistency**
- **Feature**: error-handling-refactor, Property 1
- Generate random file operation errors
- Verify all file move errors are CRITICAL
- Verify all directory cleanup errors are WARNING

**Property Test 2: Success Determination**
- **Feature**: error-handling-refactor, Property 2
- Generate random operation summaries
- Verify success is true iff no critical errors

**Property Test 3: Result Completeness**
- **Feature**: error-handling-refactor, Property 3
- Generate random file sets
- Verify all files are accounted for in results

**Property Test 4: Error Message Structure**
- **Feature**: error-handling-refactor, Property 4
- Generate random critical errors
- Verify all have messages and suggestions

**Property Test 5: Separation of Concerns**
- **Feature**: error-handling-refactor, Property 5
- Generate random operation summaries
- Verify no overlap between file errors and cleanup warnings

### Integration Tests

- Test complete folder organization flow
- Test CLI display with various result combinations
- Test backward compatibility during migration

### Test Refactoring

Update existing tests to check behavior instead of strings:

**Before:**
```python
assert "Folder cleanup complete!" in result.stdout
```

**After:**
```python
summary = parse_operation_summary(result)
assert summary.overall_success
assert summary.file_operations.files_moved > 0
```

## Migration Plan

### Step 1: Clean Up Broken Code
- Remove ALL references to `self.file_stats`, `self.directory_stats`, `self.critical_errors`, `self.warnings`
- Remove ALL imports from non-existent modules (`OperationError`, `OperationType`, etc.)
- Delete `scrubb/operation_results.py` if it exists

### Step 2: Update OrganizationStats
- Add `critical_errors: List[str]` field
- Add `warnings: List[str]` field
- Add `success` property
- Remove old `errors`, `error_files`, `directory_permission_warnings` fields

### Step 3: Update FolderOrganizer
- In `_move_file()`: Add to `stats.critical_errors` on failure
- In `_remove_empty_folders()`: Add to `stats.warnings` on permission errors
- Remove all broken code

### Step 4: Update CLI
- Check `stats.success` instead of `stats.errors`
- Display `stats.critical_errors` prominently
- Display `stats.warnings` only in verbose mode

### Step 5: Update Tests
- Update tests to check `stats.success`
- Update tests to check `len(stats.critical_errors)`
- Remove tests that check for exact strings

### Step 6: Validation
- Run full test suite
- Verify all tests pass
- Run type checking (mypy)
- Run linting (ruff)

## Performance Considerations

- Result objects are lightweight dataclasses
- No performance impact from refactor
- Clearer code may enable future optimizations

## Security Considerations

- Error messages should not expose sensitive paths
- Suggestions should not recommend unsafe operations
- Permission errors should be handled gracefully

## Future Extensions

- Add more error severities if needed
- Add error recovery strategies
- Add error reporting/telemetry
- Add user-configurable error handling
