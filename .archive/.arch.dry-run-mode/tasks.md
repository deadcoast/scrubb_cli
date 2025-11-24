# Implementation Plan

- [x] 1. Create dry-run data models





  - Create `DryRunStats` dataclass in `folder_organizer.py`
  - Create `FileOperation` dataclass for tracking planned file moves
  - Create `ConflictInfo` dataclass for tracking name conflicts
  - Create `SkippedFile` dataclass for tracking skipped files
  - Add type hints and default values using `field(default_factory=dict/list)`
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3, 8.1, 8.3_



- [x] 1.1 Write unit tests for data models




  - Test DryRunStats initialization and field defaults
  - Test FileOperation creation with and without conflicts
  - Test ConflictInfo and SkippedFile data structures
  - _Requirements: 2.1, 3.1, 4.1, 6.1_

- [x] 2. Add --dry flag to CLI




  - Add `dry` parameter to `folder()` command in `cli.py` using `typer.Option`
  - Set default value to `False` with help text "Preview changes without executing them"
  - Display prominent dry-run mode header when `dry=True`
  - Pass `dry_run` parameter to FolderOrganizer constructor
  - _Requirements: 1.1, 7.1_

- [x] 2.1 Write unit test for CLI dry flag

  - Test that --dry flag is recognized and activates dry-run mode
  - Test that dry-run header is displayed
  - _Requirements: 1.1, 7.1_

- [x] 3. Refactor FolderOrganizer for dry-run support





  - Add `dry_run: bool` parameter to `__init__` method
  - Update `organize()` to branch based on `dry_run` flag
  - Create `_organize_dry_run()` method that returns `DryRunStats`
  - Rename current organize logic to `_organize_actual()` method
  - Ensure existing functionality remains unchanged when `dry_run=False`
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 10.1, 10.2, 10.3, 10.4_

- [x] 3.1 Write unit tests for organizer refactoring


  - Test that `dry_run=False` uses actual execution path
  - Test that `dry_run=True` uses dry-run execution path
  - Test that existing functionality is not broken
  - _Requirements: 1.2, 1.3, 1.4_

- [x] 4. Implement dry-run simulation logic





  - Implement `_organize_dry_run()` method in FolderOrganizer
  - Scan files using existing `_scan_files()` method
  - Classify each file using existing classifier
  - Track skipped files with unknown extensions
  - Simulate destination paths for each file
  - Detect and track name conflicts
  - Record all file operations in DryRunStats
  - Track directories that would be created
  - _Requirements: 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.5, 4.1, 6.1, 10.1_

- [x] 4.1 Implement conflict simulation


  - Create `_simulate_destination()` method to calculate destination paths
  - Create `_would_conflict()` method to check for conflicts without file system access
  - Create `_simulate_conflict_resolution()` method to generate resolved names
  - Maintain set of simulated destinations to detect conflicts within same run
  - Track conflicts in `ConflictInfo` objects
  - _Requirements: 4.1, 4.2, 4.3, 10.2_

- [x] 4.2 Implement empty directory identification


  - Create `_identify_empty_directories()` method
  - Simulate which directories would become empty after file moves
  - Exclude root directory and Scrubbed folder from removal list
  - Return list of directories that would be removed
  - Track count in DryRunStats
  - _Requirements: 3.3, 3.4, 10.3_

- [x] 4.3 Implement potential error detection


  - Create `_check_potential_errors()` method
  - Check read permissions on each file
  - Catch and record PermissionError exceptions
  - Catch and record other access exceptions
  - Return list of error messages
  - Track in DryRunStats.potential_errors
  - _Requirements: 8.1, 8.3_

- [x] 4.4 Write property test for no file system modifications


  - **Property 1: No file system modifications in dry-run mode**
  - **Validates: Requirements 1.2, 1.3, 1.4**
  - Generate random directory structures with files
  - Capture initial file system state
  - Run dry-run mode
  - Verify no directories created, no files moved, no directories deleted
  - Use Hypothesis to generate directory structures

- [x] 4.5 Write property test for classification consistency


  - **Property 9: Classification consistency**
  - **Validates: Requirements 10.1**
  - Generate random files with various extensions
  - Run classification in both dry-run and actual mode contexts
  - Verify identical categorization results
  - Use Hypothesis to generate file names and extensions

- [x] 4.6 Write property test for conflict resolution consistency


  - **Property 10: Conflict resolution consistency**
  - **Validates: Requirements 10.2**
  - Generate files with duplicate names
  - Compare conflict resolution in dry-run vs actual mode
  - Verify identical resolved filenames
  - Use Hypothesis to generate conflicting file names

- [x] 4.7 Write property test for empty directory detection consistency


  - **Property 11: Empty directory detection consistency**
  - **Validates: Requirements 10.3**
  - Generate directory structures that become empty after moves
  - Compare empty directory detection in dry-run vs actual mode
  - Verify identical directory lists
  - Use Hypothesis to generate directory structures

- [x] 5. Create output formatter for dry-run results





  - Create `DryRunFormatter` class in `folder_organizer.py`
  - Implement `format_output()` static method
  - Create header section with dry-run indicator
  - Create summary statistics section
  - Create files by category section
  - Create directories to create section
  - Create file operations section grouped by category
  - Create conflicts section
  - Create skipped files section
  - Create empty directories to remove section
  - Create potential errors section
  - Create footer with reminder that no changes were made
  - Use clear section headers and consistent formatting
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 7.2, 7.3, 8.1, 8.3, 9.1, 9.4_

- [x] 5.1 Write unit tests for output formatter


  - Test that all sections are present in output
  - Test formatting of file operations
  - Test formatting of conflicts
  - Test formatting of skipped files
  - Test formatting of potential errors
  - Test edge cases (no conflicts, no errors, no skipped files)
  - _Requirements: 9.1, 9.4_

- [x] 5.2 Write property test for complete file operation reporting


  - **Property 2: Complete file operation reporting**
  - **Validates: Requirements 2.1, 2.2, 2.3**
  - Generate random file sets with various extensions
  - Run dry-run mode
  - Verify all moveable files are listed in output with source and destination
  - Use Hypothesis to generate file sets

- [x] 5.3 Write property test for accurate statistics reporting

  - **Property 3: Accurate statistics reporting**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
  - Generate random directory structures
  - Run dry-run mode
  - Verify statistics match expected counts for all categories
  - Use Hypothesis to generate directory structures

- [x] 5.4 Write property test for conflict detection and reporting

  - **Property 4: Conflict detection and reporting**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
  - Generate files with duplicate names
  - Run dry-run mode
  - Verify all conflicts are detected and reported with original and resolved names
  - Use Hypothesis to generate conflicting file names


- [x] 5.5 Write property test for directory creation reporting
  - **Property 5: Directory creation reporting**
  - **Validates: Requirements 5.1, 5.2, 5.4**
  - Generate files requiring various categories
  - Run dry-run mode
  - Verify all necessary directories are listed in output
  - Use Hypothesis to generate file sets

- [x] 5.6 Write property test for skipped file reporting

  - **Property 6: Skipped file reporting**
  - **Validates: Requirements 6.1, 6.2, 6.3**
  - Generate files with unknown extensions
  - Run dry-run mode
  - Verify all skipped files are listed with paths and reasons
  - Use Hypothesis to generate file names with unknown extensions

- [x] 5.7 Write property test for potential error detection

  - **Property 7: Potential error detection**
  - **Validates: Requirements 8.1, 8.3**
  - Generate files with simulated permission issues
  - Run dry-run mode
  - Verify potential errors are detected and reported with accurate count
  - Use mocking to simulate permission errors


- [x] 5.8 Write property test for output organization
  - **Property 8: Output organization**
  - **Validates: Requirements 9.1, 9.4**
  - Generate various directory structures
  - Run dry-run mode
  - Verify output contains all required sections with consistent formatting
  - Use Hypothesis to generate directory structures

- [x] 6. Integrate dry-run output with CLI





  - Update `folder()` command in `cli.py` to handle DryRunStats
  - Call `DryRunFormatter.format_output()` when dry-run mode is active
  - Display formatted output using `typer.echo()`
  - Display completion message reminding user no changes were made
  - Ensure regular mode output remains unchanged
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 6.1 Write unit tests for CLI integration


  - Test that dry-run output is displayed correctly
  - Test that completion message is shown
  - Test that regular mode is not affected
  - _Requirements: 7.1, 7.2_

- [x] 7. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Write comprehensive round-trip property test





  - **Property 12: Dry-run prediction accuracy**
  - **Validates: Requirements 10.4**
  - Generate random directory structures
  - Run dry-run mode to capture predictions
  - Create a copy of the directory structure
  - Run actual mode on the copy
  - Compare actual results with dry-run predictions
  - Verify file destinations match predictions
  - Verify conflict resolutions match predictions
  - Verify empty directories removed match predictions
  - Use Hypothesis to generate directory structures
  - _Requirements: 10.4_

- [x] 9. Update documentation





  - Update README.md with dry-run mode description
  - Add usage examples for `scrubb --folder --dry` command
  - Document the additional information provided in dry-run mode
  - Add comparison between regular and dry-run modes
  - Update COMMAND_REFERENCE.md with --dry flag details
  - Update OVERVIEW.md to mention dry-run capability

- [x] 10. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
