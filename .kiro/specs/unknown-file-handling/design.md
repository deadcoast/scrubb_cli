# Design Document

## Overview

This design addresses two critical issues in the Scrubb folder organization feature:
1. Files with unknown extensions are currently skipped instead of being organized
2. The folder organization pipeline may have integration issues preventing proper execution

The solution adds an "Other" category for unknown file types and ensures robust end-to-end functionality with comprehensive logging and error handling.

## Architecture

The folder organization system consists of three main layers:

1. **CLI Layer** (`cli.py`): Handles user interaction, path validation, and command orchestration
2. **Classification Layer** (`file_classifier.py`): Categorizes files based on extensions
3. **Organization Layer** (`folder_organizer.py`): Executes file moves and directory cleanup

The fix involves:
- Adding `FileCategory.OTHER` to the classification layer
- Updating the classifier to return `OTHER` instead of `UNKNOWN` for unrecognized extensions
- Ensuring the organizer processes `OTHER` category files
- Adding logging throughout the pipeline for debugging

## Components and Interfaces

### FileCategory Enum

```python
class FileCategory(Enum):
    IMAGE = "Images"
    VIDEO = "Video"
    MARKDOWN = "Docs/Markdown"
    DOCUMENT = "Docs/Other Docs"
    DEVELOPMENT = "Development"
    OTHER = "Other"  # NEW: replaces UNKNOWN
```

### FileClassifier

**Modified Method:**
```python
def classify(self, file_path: Path) -> FileCategory:
    """
    Classify a file based on its extension.
    Returns FileCategory.OTHER for unknown extensions instead of UNKNOWN.
    """
```

**Behavior Change:**
- Previously: Returned `FileCategory.UNKNOWN` for unrecognized extensions
- Now: Returns `FileCategory.OTHER` for unrecognized extensions
- Files with no extension return `FileCategory.OTHER`

### FolderOrganizer

**Modified Logic:**
- Remove the check that skips `FileCategory.UNKNOWN` files
- Process `FileCategory.OTHER` files like any other category
- Create "Other" folder in the Scrubbed directory
- Move unknown extension files to "Other" folder

**Dry-Run Mode:**
- Include `OTHER` category files in statistics
- Display `OTHER` category in file operations preview
- Show count of files in `OTHER` category

### CLI Integration

**Enhanced Logging:**
- Log directory path being processed
- Log number of files discovered during scan
- Log category assignments in verbose mode
- Log completion statistics

**Error Handling:**
- Capture and display specific error messages
- Show file paths for failed operations
- Provide actionable error messages

## Data Models

### OrganizationStats

No changes needed - already tracks files by category using dictionary.

### DryRunStats

No changes needed - already includes:
- `files_by_category: Dict[str, int]` - will include "Other" category
- `skipped_files: List[SkippedFile]` - will be empty for unknown extensions
- `file_operations: List[FileOperation]` - will include OTHER category operations

### FileOperation

No changes needed - already supports any FileCategory value.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete file coverage

*For any* directory containing files, after organization completes, the number of files in categorized folders plus files that failed to move SHALL equal the total number of files discovered during scanning.

**Validates: Requirements 1.1, 1.4, 3.3**

### Property 2: OTHER category assignment

*For any* file with an extension not in the predefined category mappings, the FileClassifier SHALL return FileCategory.OTHER.

**Validates: Requirements 1.1, 2.3**

### Property 3: No files skipped for unknown extensions

*For any* file classified as FileCategory.OTHER, the FolderOrganizer SHALL include it in file operations and SHALL NOT add it to the skipped files list.

**Validates: Requirements 1.3, 1.4**

### Property 4: Statistics completeness

*For any* organization operation (dry-run or actual), the statistics SHALL include a count for the "Other" category if any files with unknown extensions were processed.

**Validates: Requirements 1.5, 2.2**

### Property 5: Dry-run consistency

*For any* directory, running in dry-run mode SHALL produce statistics that match what would happen in actual mode, including OTHER category files.

**Validates: Requirements 1.3, 2.1**

### Property 6: Category folder creation

*For any* file category with at least one file to move, the system SHALL create the corresponding category folder in the Scrubbed directory.

**Validates: Requirements 1.2, 3.4**

### Property 7: Error reporting completeness

*For any* file operation that fails, the system SHALL add the file path to the error list and increment the error count.

**Validates: Requirements 4.4**

## Error Handling

### File Classification Errors

- **No extension**: Treat as OTHER category
- **Permission denied**: Log error, add to error list, continue processing other files
- **File not found**: Log error, add to error list, continue processing

### File Organization Errors

- **Permission denied on move**: Log error with file path, increment error count, continue
- **Destination already exists**: Use conflict resolution (append counter), log if verbose
- **Disk full**: Capture OS error, display to user, halt operation

### CLI Errors

- **Invalid path**: Display error message with suggestion, exit with code 2
- **Path not a directory**: Display error message with suggestion, exit with code 2
- **Empty directory**: Complete successfully with message "No files to organize"

### Logging Strategy

**Normal Mode:**
- Display target directory
- Display summary statistics
- Display errors

**Verbose Mode:**
- Display target directory
- Display files discovered count
- Display each file's category assignment
- Display each file move operation
- Display summary statistics
- Display errors

**Quiet Mode:**
- Display only errors

## Testing Strategy

### Unit Tests

1. **Test FileClassifier with unknown extensions**
   - Test various unknown extensions return OTHER
   - Test files with no extension return OTHER
   - Test known extensions still return correct categories

2. **Test FolderOrganizer processes OTHER category**
   - Test OTHER category files are moved to "Other" folder
   - Test OTHER category appears in statistics
   - Test OTHER category files not in skipped list

3. **Test dry-run includes OTHER category**
   - Test dry-run statistics include OTHER category count
   - Test dry-run file operations include OTHER category files
   - Test dry-run doesn't skip unknown extensions

### Property-Based Tests

We will use **Hypothesis** for property-based testing in Python. Each property-based test will run a minimum of 100 iterations.

Each property-based test MUST be tagged with a comment explicitly referencing the correctness property from this design document using the format: `**Feature: unknown-file-handling, Property {number}: {property_text}**`

1. **Property 1: Complete file coverage**
   - Generate random directory structures with mixed file types
   - Run organization
   - Verify: files_moved + errors == total_files_discovered

2. **Property 2: OTHER category assignment**
   - Generate random file extensions (not in known categories)
   - Classify each file
   - Verify: all return FileCategory.OTHER

3. **Property 3: No files skipped for unknown extensions**
   - Generate files with random unknown extensions
   - Run dry-run organization
   - Verify: skipped_files list is empty for these files
   - Verify: files appear in file_operations list

4. **Property 4: Statistics completeness**
   - Generate directory with at least one unknown extension file
   - Run organization
   - Verify: "Other" appears in files_by_category

5. **Property 5: Dry-run consistency**
   - Generate random directory structure
   - Run dry-run and capture statistics
   - Run actual mode and capture statistics
   - Verify: files_to_move == files_moved (accounting for errors)
   - Verify: category counts match

6. **Property 6: Category folder creation**
   - Generate files for random subset of categories
   - Run organization
   - Verify: folder exists for each category with files
   - Verify: "Other" folder exists if unknown extension files present

7. **Property 7: Error reporting completeness**
   - Generate files with simulated permission errors
   - Run organization
   - Verify: error_files list contains all failed files
   - Verify: error count matches error_files length

### Integration Tests

1. **End-to-end folder command test**
   - Create test directory with mixed file types including unknown extensions
   - Run `scrubb folder` command
   - Verify all files organized including unknown extensions
   - Verify statistics displayed correctly

2. **Dry-run to actual consistency test**
   - Run dry-run mode
   - Capture predicted statistics
   - Run actual mode
   - Verify actual results match predictions

3. **Error handling test**
   - Create files with permission issues
   - Run folder command
   - Verify errors reported correctly
   - Verify other files still processed

## Implementation Notes

### Migration Strategy

1. Add `OTHER` category to `FileCategory` enum
2. Update `FileClassifier.classify()` to return `OTHER` instead of `UNKNOWN`
3. Remove skip logic for `UNKNOWN` category in `FolderOrganizer`
4. Update dry-run formatter to handle `OTHER` category
5. Add logging statements throughout pipeline
6. Update tests to cover new behavior

### Backward Compatibility

- The `UNKNOWN` category can be deprecated but kept for backward compatibility
- Existing code checking for `UNKNOWN` will need to be updated to check for `OTHER`
- Configuration files and saved state do not reference categories, so no migration needed

### Performance Considerations

- No performance impact - same number of file operations
- Slightly more files moved (previously skipped files now moved)
- Logging in verbose mode may slow execution slightly

## Dependencies

- No new external dependencies required
- Uses existing Python standard library modules
- Uses existing Hypothesis library for property-based testing
