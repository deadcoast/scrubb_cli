# Implementation Plan

- [x] 1. Create file classification module





  - Create `scrubb/file_classifier.py` with FileCategory enum and FileClassifier class
  - Implement extension mappings for all file categories (images, video, markdown, documents, development)
  - Implement `classify()` method to determine file category based on extension
  - Handle case-insensitive extension matching
  - Return UNKNOWN category for unrecognized or missing extensions
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 1.1 Write unit tests for file classifier


  - Test classification of each file type category with sample extensions
  - Test handling of files with no extension
  - Test handling of files with unrecognized extensions
  - Test case-insensitive extension matching (.JPG vs .jpg)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 2. Create folder organization module





  - Create `scrubb/folder_organizer.py` with OrganizationStats dataclass and FolderOrganizer class
  - Implement `__init__()` to set up root path, scrubbed path, and classifier
  - Implement `organize()` as main entry point that orchestrates the full process
  - _Requirements: 3.6, 7.1_

- [x] 2.1 Implement file scanning functionality


  - Implement `_scan_files()` to recursively discover all files in root directory
  - Exclude files already in the Scrubbed folder from scanning
  - Handle nested directories at all depth levels
  - _Requirements: 7.1, 7.2_

- [x] 2.2 Write property test for recursive file discovery


  - **Property 8: Recursive file discovery**
  - **Validates: Requirements 7.1, 7.2**
  - Generate random nested directory structures with files at various depths
  - Verify all files are discovered regardless of nesting level
  - Use Hypothesis to generate directory structures

- [x] 2.3 Implement file moving functionality


  - Implement `_move_file()` to move a file to its category folder
  - Create category subdirectories as needed
  - Handle file name conflicts by calling conflict resolution
  - Track statistics (files moved, category counts)
  - Handle errors gracefully and continue processing
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, 9.1, 9.2_

- [x] 2.4 Write property test for file categorization correctness


  - **Property 1: File categorization correctness**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
  - Generate random files with various recognized extensions
  - Verify each file ends up in the correct category folder
  - Use Hypothesis to generate file names and extensions

- [x] 2.5 Write property test for category directory creation


  - **Property 3: Category directory creation**
  - **Validates: Requirements 3.7**
  - Generate random sets of files requiring different categories
  - Verify all necessary category directories are created
  - Use Hypothesis to generate file sets

- [x] 2.6 Write property test for directory structure flattening


  - **Property 9: Directory structure flattening**
  - **Validates: Requirements 7.3**
  - Generate files in nested source directories
  - Verify destination has flat structure organized by category only
  - Use Hypothesis to generate nested structures

- [x] 2.7 Write property test for error handling continuation


  - **Property 10: Error handling continuation**
  - **Validates: Requirements 9.1, 9.2**
  - Simulate file access errors during processing
  - Verify processing continues and errors are properly tracked
  - Use mocking to simulate permission errors

- [x] 2.8 Implement name conflict resolution

  - Implement `_handle_name_conflict()` to generate unique filenames
  - Append numeric suffixes (1, 2, 3, ...) for conflicts
  - Preserve original file extensions
  - Handle multiple conflicts with incrementing numbers
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 2.9 Write property test for name conflict resolution


  - **Property 4: Name conflict resolution preserves files**
  - **Validates: Requirements 4.1, 4.3**
  - Generate files with conflicting names
  - Verify all files exist after move with correct extensions preserved
  - Use Hypothesis to generate file names

- [x] 2.10 Write property test for incremental conflict numbering


  - **Property 5: Incremental conflict numbering**
  - **Validates: Requirements 4.2**
  - Generate multiple files with identical names
  - Verify numbering is sequential (file.txt, file_1.txt, file_2.txt, ...)
  - Use Hypothesis to generate duplicate file names

- [x] 2.11 Implement empty folder removal


  - Implement `_is_empty_directory()` to check if directory is empty or contains only empty subdirs
  - Implement `_remove_empty_folders()` to recursively remove empty directories
  - Use bottom-up traversal for efficiency
  - Protect root directory and Scrubbed folder from deletion
  - Track count of removed directories
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2.12 Write property test for empty directory removal


  - **Property 6: Empty directory removal**
  - **Validates: Requirements 5.1**
  - Generate directory structures that become empty after file moves
  - Verify empty directories are removed (except protected ones)
  - Use Hypothesis to generate directory structures

- [x] 2.13 Write property test for recursive empty directory removal


  - **Property 7: Recursive empty directory removal**
  - **Validates: Requirements 5.2**
  - Generate nested empty directory structures
  - Verify all empty subdirectories are removed recursively
  - Verify root and Scrubbed folders are protected
  - Use Hypothesis to generate nested structures

- [x] 3. Add folder command to CLI





  - Add new `folder()` command to `scrubb/cli.py` using Typer
  - Implement interactive prompt for directory path using `typer.prompt()`
  - Validate that provided path exists and is a directory
  - Handle path resolution (absolute, relative, tilde expansion)
  - Display error message and exit gracefully for invalid paths
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4_

- [x] 3.1 Write property test for path resolution consistency


  - **Property 2: Path resolution consistency**
  - **Validates: Requirements 2.1, 2.3**
  - Generate various path formats (absolute, relative, with tilde)
  - Verify operations occur within the correctly resolved path
  - Use Hypothesis to generate path strings

- [x] 3.2 Integrate FolderOrganizer with CLI command

  - Instantiate FileClassifier and FolderOrganizer in folder command
  - Call `organize()` method to execute cleanup
  - Capture and display OrganizationStats after completion
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 3.3 Implement statistics display

  - Format and display total files moved
  - Display files moved per category with category names
  - Display number of empty folders removed
  - Display error count and list of error files
  - Use colored output for better readability (green for success, red for errors)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 3.4 Write unit tests for CLI folder command

  - Test folder command invocation
  - Test path validation (valid and invalid paths)
  - Test statistics display format
  - Test mode exclusivity (folder mode doesn't trigger emoji scrubbing)
  - _Requirements: 1.1, 1.2, 1.3, 2.2, 6.1, 6.2, 6.3, 6.4_

- [x] 4. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Update documentation





  - Update README.md with folder cleanup feature description
  - Add usage examples for `scrubb --folder` command
  - Document file type categories and their extensions
  - Add folder cleanup workflow explanation
  - Update COMMAND_REFERENCE.md with folder command details
  - Update OVERVIEW.md to mention both features

- [x] 6. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
