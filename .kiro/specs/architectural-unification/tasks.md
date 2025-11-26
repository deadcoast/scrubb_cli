= Implementation Plan: Architectural Unification

This implementation plan transforms the scrubb codebase from a collection of quick fixes into a professional, maintainable system. Each task builds incrementally, with checkpoints to ensure correctness.

## Phase 1: Foundation - Core Architecture

- [x] 1. Create new module structure





  - Create `scrubb/core/` directory
  - Create `scrubb/io/` directory
  - Create `scrubb/business/` directory
  - Create `scrubb/cli/` directory
  - Create `scrubb/legacy/` directory for backward compatibility
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 1.1 Implement core interfaces


  - Create `scrubb/core/interfaces.py`
  - Define `FileOperations` protocol
  - Define `DirectoryOperations` protocol
  - Define `FileClassifier` protocol
  - Define `ConflictResolver` protocol
  - Define `TreeRenderer` protocol
  - Define `PathValidator` protocol
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 1.2 Implement result types


  - Create `scrubb/core/result.py`
  - Implement `Success[T]` class
  - Implement `Failure[T]` class
  - Implement `Result[T]` type alias
  - Implement `OperationResult` dataclass
  - Add `unwrap()` and `unwrap_or()` methods
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 1.3 Implement error hierarchy


  - Create `scrubb/core/errors.py`
  - Implement `ScrubbError` base exception
  - Implement `ValidationError` exception
  - Implement `ConfigurationError` exception
  - Implement `FileOperationError` exception
  - Implement `DirectoryOperationError` exception
  - Implement `PathSecurityError` exception
  - Implement `ClassificationError` exception
  - Add context dictionary to all exceptions
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 1.4 Implement constants


  - Create `scrubb/core/constants.py`
  - Define exit code constants (EXIT_SUCCESS, EXIT_ERROR, etc.)
  - Define file size unit constants (BYTES_PER_KB, etc.)
  - Define default limit constants (MAX_FILES_PER_DIR_DISPLAY, etc.)
  - Define configuration key constants
  - Implement `OperationStatus` enum
  - Implement `ErrorSeverity` enum
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [x] 1.5 Implement validation module


  - Create `scrubb/core/validation.py`
  - Implement input validation functions
  - Implement path validation functions
  - Implement configuration validation functions
  - Add validation error messages
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 1.6 Write property test for core types






  - **Property 4: Error Propagation**
  - **Validates: Requirements 4.1**
  - Test that invalid input raises exceptions immediately
  - Test that Result types properly wrap success/failure
  - Test that error context is preserved

## Phase 2: I/O Layer Implementation

- [x] 2. Implement file operations





  - Create `scrubb/io/file_operations.py`
  - Implement `RealFileOperations` class
  - Implement `read_file()` method returning Result
  - Implement `write_file()` method returning Result
  - Implement `move_file()` method returning Result
  - Implement `delete_file()` method returning Result
  - Implement `file_exists()` method
  - Implement `get_file_size()` method returning Result
  - Handle all exceptions and return Failure results
  - _Requirements: 2.3, 4.1, 4.2_

- [x] 2.1 Implement directory operations





  - Create `scrubb/io/directory_operations.py`
  - Implement `RealDirectoryOperations` class
  - Implement `create_directory()` method returning Result
  - Implement `remove_directory()` method returning Result
  - Implement `list_directory()` method returning Result
  - Implement `is_empty()` method returning Result (O(1) check)
  - Implement `directory_exists()` method
  - Handle all exceptions and return Failure results
  - _Requirements: 2.3, 3.1, 4.1, 4.2_

- [x] 2.2 Implement path validator


  - Create `scrubb/io/path_validator.py`
  - Implement `PathValidator` class
  - Implement `validate()` method checking path is within root
  - Implement `resolve()` method resolving user paths safely
  - Check for `..` traversal attempts
  - Check for null bytes and special characters
  - Check for symlink targets outside root
  - Return PathSecurityError for violations
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 2.3 Write property test for path validation
  - **Property 7: Path Security**
  - **Validates: Requirements 7.1**
  - Generate random paths with traversal attempts
  - Verify all traversal attempts are rejected
  - Verify valid paths are accepted

- [ ]* 2.4 Write unit tests for I/O layer
  - Test file operations with temporary files
  - Test directory operations with temporary directories
  - Test error handling for permission errors
  - Test error handling for missing files/directories
  - _Requirements: 2.3, 4.1_

- [ ] 3. Checkpoint - Ensure I/O layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Business Logic Layer

- [x] 4. Implement enhanced file classifier





  - Create `scrubb/business/classifier.py`
  - Implement `ClassificationRule` dataclass
  - Implement `EnhancedFileClassifier` class
  - Implement `classify()` method
  - Implement `get_category_name()` method
  - Implement `_default_rules()` static method
  - Support priority-based rule ordering
  - Support configurable rules
  - _Requirements: 11.3, 12.1, 12.2_

- [x] 4.1 Implement conflict resolver


  - Create `scrubb/business/conflict_resolver.py`
  - Implement `ConflictResolver` class
  - Implement `resolve()` method generating unique names
  - Use numeric suffixes for conflicts
  - Preserve file extensions
  - Handle multiple conflicts efficiently
  - _Requirements: 1.5, 3.4_

- [x] 4.2 Implement file organizer


  - Create `scrubb/business/organizer.py`
  - Implement `OrganizationPlan` dataclass
  - Implement `FileOrganizer` class with dependency injection
  - Implement `plan_organization()` method (O(n) algorithm)
  - Implement `execute_plan()` method
  - Implement `_is_in_scrubbed_folder()` helper
  - Implement `_will_be_empty()` helper (O(1) per directory)
  - Use single-pass traversal for file collection
  - Use bottom-up traversal for empty directory detection
  - _Requirements: 3.1, 3.2, 3.3, 10.1, 10.2_

- [x] 4.3 Write property test for algorithm efficiency






  - **Property 3: Algorithm Efficiency**
  - **Validates: Requirements 3.1**
  - Generate random directory structures
  - Measure time complexity empirically
  - Verify O(n) behavior for large inputs

- [x] 4.4 Write property test for organization correctness






  - **Property 6: Simulation Accuracy**
  - **Validates: Requirements 6.1**
  - Generate random file sets
  - Plan organization
  - Verify all files are accounted for
  - Verify no files are lost



- [x] 4.5 Implement tree builder





  - Create `scrubb/business/tree_builder.py`
  - Implement `TreeBuilder` class
  - Implement `build_tree()` method creating DirectoryNode tree
  - Implement `simulate_after_state()` method (no filesystem access)
  - Implement `_remove_moved_files()` helper
  - Implement `_add_scrubbed_folder()` helper
  - Implement `_remove_empty_dirs()` helper


  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 4.6 Implement statistics calculator





  - Create `scrubb/business/statistics.py`
  - Implement `StatisticsCalculator` class
  - Implement `calculate()` method (single traversal)
  - Remove all try-except blocks around arithmetic


  - Validate input data at boundaries
  - Fail fast on invalid data
  - _Requirements: 4.1, 4.2, 4.3, 9.1, 9.2_

- [x] 4.7 Implement emoji detector





  - Create `scrubb/business/emoji_detector.py`
  - Implement `EmojiDetector` class
  - Fix emoji regex to remove overlapping ranges
  - Use grapheme cluster detection library (grapheme or emoji)
  - Implement `detect()` method returning list of emoji positions
  - Implement `remove()` method removing emojis
  - Implement `count()` method counting grapheme clusters
  - Validate regex at module load time
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 4.8 Write property test for emoji detection







  - **Property 8: Emoji Detection Completeness**
  - **Validates: Requirements 8.1**
  - Generate random text with emojis
  - Verify all emojis are detected
  - Verify grapheme clusters are counted correctly

- [ ]* 4.9 Write unit tests for business logic
  - Test classifier with various file extensions
  - Test conflict resolver with multiple conflicts
  - Test organizer with various directory structures
  - Test tree builder simulation accuracy
  - Test statistics calculator with edge cases
  - Test emoji detector with various emoji types
  - _Requirements: 3.1, 6.1, 8.1_

- [x] 5. Checkpoint - Ensure business logic tests pass





  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: CLI Layer Implementation

- [ ] 6. Extract shared CLI utilities





  - Create `scrubb/cli/shared.py`
  - Extract verbosity setup into `setup_verbosity()` function
  - Extract error handling into `handle_error()` function
  - Extract path resolution into `resolve_path()` function
  - Extract confirmation prompts into `confirm_operation()` function
  - Remove ALL code duplication from cli.py
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 6.1 Implement output formatting


  - Create `scrubb/cli/output.py`
  - Implement `OutputFormatter` class with dependency injection
  - Implement `format_operation_result()` method
  - Implement `format_error()` method
  - Implement `format_warning()` method
  - Implement `format_statistics()` method
  - Use consistent formatting throughout
  - _Requirements: 2.1, 17.1, 17.2_



- [x] 6.2 Implement input handling

  - Create `scrubb/cli/input.py`
  - Implement `InputHandler` class
  - Implement `prompt_for_path()` method with validation
  - Implement `prompt_for_confirmation()` method
  - Implement `validate_path_input()` method


  - Use PathValidator for security
  - _Requirements: 7.1, 15.1, 15.2_

- [x] 6.3 Implement command handlers

  - Create `scrubb/cli/commands.py`
  - Implement `EmojiCommand` class
  - Implement `FolderCommand` class
  - Implement `StatsCommand` class

  - Implement `ConfigCommand` class
  - Use dependency injection for all dependencies
  - Separate command logic from Typer decorators
  - _Requirements: 2.1, 2.2, 10.1, 10.2_

- [x] 6.4 Refactor main CLI module

  - Update `scrubb/cli.py` to use new command handlers
  - Remove all duplicated code
  - Use shared utilities for common operations
  - Inject dependencies into command handlers
  - Keep only Typer app configuration and routing
  - _Requirements: 1.1, 1.2, 1.3, 2.1_

- [ ]* 6.5 Write property test for layer separation
  - **Property 2: Layer Separation**
  - **Validates: Requirements 2.1**
  - Verify CLI doesn't directly access file system
  - Verify CLI calls business logic through interfaces
  - Verify business logic doesn't import CLI modules

- [ ]* 6.6 Write unit tests for CLI layer
  - Test command handlers with mocked dependencies
  - Test output formatting with various results
  - Test input handling with various inputs
  - Test error handling with various errors
  - _Requirements: 2.1, 2.4_

- [ ] 7. Checkpoint - Ensure CLI tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: Integration and Migration

- [ ] 8. Implement configuration validation
  - Update `scrubb/config.py`
  - Add schema validation for configuration
  - Validate all required fields
  - Validate all field types
  - Validate paths exist and are accessible
  - Validate patterns are valid regex
  - Raise ConfigurationError for invalid config
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 8.1 Implement structured logging
  - Create `scrubb/core/logging.py`
  - Configure Python logging module
  - Add structured logging with context
  - Support DEBUG, INFO, WARNING, ERROR levels
  - Integrate with verbosity manager
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 8.2 Update existing modules to use new architecture
  - Update `scrubb/scrubber.py` to use EmojiDetector
  - Update `scrubb/folder_organizer.py` to use FileOrganizer
  - Update `scrubb/tree_visualizer.py` to use TreeBuilder
  - Update `scrubb/directory_scanner.py` to use DirectoryOperations
  - Update `scrubb/statistics_calculator.py` to use new implementation
  - _Requirements: 24.2, 24.3_

- [ ] 8.3 Write integration tests
  - Create `tests/integration/` directory
  - Test complete folder organization workflow
  - Test complete emoji scrubbing workflow
  - Test complete tree visualization workflow
  - Test dry-run mode accuracy
  - Test error handling end-to-end
  - Use temporary directories for all tests
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [ ]* 8.4 Write property tests for integration
  - **Property 1: Code Duplication Elimination**
  - **Validates: Requirements 1.1**
  - Scan codebase for duplicate code patterns
  - Verify no duplicate implementations exist

- [ ]* 8.5 Write property tests for type consistency
  - **Property 5: Type Consistency**
  - **Validates: Requirements 5.1**
  - Run mypy on entire codebase
  - Verify zero type errors

- [ ]* 8.6 Write property tests for exception specificity
  - **Property 9: Exception Specificity**
  - **Validates: Requirements 9.1**
  - Scan codebase for bare except clauses
  - Verify all exceptions are specific

- [ ]* 8.7 Write property tests for dependency injection
  - **Property 10: Dependency Injection**
  - **Validates: Requirements 10.1**
  - Verify all components accept dependencies via constructor
  - Verify no global state is used

- [ ] 9. Checkpoint - Ensure all integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: Performance and Quality

- [ ] 10. Implement performance benchmarks
  - Create `tests/benchmarks/` directory
  - Benchmark file scanning with various directory sizes
  - Benchmark empty directory detection with various depths
  - Benchmark tree rendering with various tree sizes
  - Measure mean, median, and standard deviation
  - Set performance regression thresholds
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

- [ ] 10.1 Implement code quality gates
  - Create `.pre-commit-config.yaml`
  - Configure mypy for type checking
  - Configure ruff for linting
  - Configure black for formatting
  - Configure bandit for security checks
  - Add pre-commit hooks
  - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_

- [ ] 10.2 Implement CI configuration
  - Create `.github/workflows/ci.yml`
  - Run unit tests on push
  - Run property-based tests on push
  - Run integration tests on push
  - Run quality checks on push
  - Run performance benchmarks on push
  - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_

- [ ] 10.3 Update documentation
  - Update `docs/ARCHITECTURE.md` with new architecture
  - Update `docs/COMMAND_REFERENCE.md` with new commands
  - Update `docs/dev/CONTRIBUTING.md` with new guidelines
  - Update `README.md` with new features
  - Add docstrings to all public APIs
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [ ] 10.4 Update CHANGELOG
  - Add version 2.0.0 section
  - Document breaking changes
  - Document new features
  - Document bug fixes
  - Document performance improvements
  - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_

- [ ] 11. Checkpoint - Ensure all quality gates pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: Cleanup and Release

- [ ] 12. Remove deprecated code
  - Move old implementations to `scrubb/legacy/`
  - Remove all backward compatibility shims
  - Remove all TODO/FIXME comments
  - Remove all unused imports
  - Remove all dead code
  - _Requirements: 24.4_

- [ ] 12.1 Final validation
  - Run full test suite
  - Run all quality checks
  - Run all performance benchmarks
  - Verify zero mypy errors
  - Verify zero ruff warnings
  - Verify all tests pass
  - _Requirements: 21.1, 21.2, 21.3, 22.1, 22.2, 22.3_

- [ ] 12.2 Create release
  - Tag version 2.0.0
  - Create GitHub release
  - Write release notes
  - Document migration guide
  - Update documentation
  - _Requirements: 23.1, 23.2, 23.3_

- [ ] 12.3 Implement rollback strategy
  - Document rollback procedure
  - Create rollback script
  - Test rollback procedure
  - Document recovery steps
  - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5_

- [ ] 13. Final Checkpoint - Release validation
  - Ensure all tests pass, ask the user if questions arise.
  - Verify release is ready for deployment.
