# Requirements Document: Error Handling Architecture Refactor

## Introduction

The current error handling system in the folder organizer has fundamental architectural flaws that lead to poor user experience and brittle tests. This spec defines requirements for a complete refactor that separates concerns, provides clear error classification, and creates a maintainable, extensible codebase.

## Glossary

- **System**: The folder organization application (scrubb)
- **Critical Error**: An error that prevents the primary feature (file organization) from working
- **Warning**: An issue that doesn't prevent the primary feature from working (e.g., directory cleanup failures)
- **Operation Result**: A structured data type representing the outcome of an operation
- **Error Classification**: The process of categorizing errors by severity and impact
- **Legacy Stats**: The old OrganizationStats dataclass that conflates all errors
- **Operation Summary**: The new structured result type that separates critical errors from warnings

## Requirements

### Requirement 1: Single Source of Truth for Results

**User Story:** As a developer, I want a single, clear data structure for operation results, so that I don't have duplicate tracking systems causing confusion.

#### Acceptance Criteria

1. WHEN the system performs file operations, THEN the system SHALL use exactly one result tracking mechanism
2. WHEN operation results are recorded, THEN the system SHALL NOT maintain duplicate statistics in multiple data structures
3. WHEN developers query operation results, THEN the system SHALL provide a single, authoritative source for all operation outcomes
4. WHEN the refactor is complete, THEN the system SHALL have removed the OrganizationStats dataclass entirely
5. WHEN the refactor is complete, THEN the system SHALL use only OperationSummary for result tracking

### Requirement 2: Clear Error Classification

**User Story:** As a user, I want to understand which errors are critical and which are just warnings, so that I know if my files were actually organized successfully.

#### Acceptance Criteria

1. WHEN a file move fails, THEN the system SHALL classify it as a CRITICAL error
2. WHEN a directory removal fails due to permissions, THEN the system SHALL classify it as a WARNING
3. WHEN displaying results, THEN the system SHALL clearly separate critical errors from warnings
4. WHEN the operation completes, THEN the system SHALL indicate success if files were moved, even if directory cleanup had warnings
5. WHEN displaying warnings, THEN the system SHALL include context explaining why they don't indicate failure

### Requirement 3: Behavior-Based Testing

**User Story:** As a developer, I want tests that verify behavior rather than exact output strings, so that tests don't break when we improve messaging.

#### Acceptance Criteria

1. WHEN tests verify operation success, THEN tests SHALL check for successful file moves, not specific message strings
2. WHEN tests verify error handling, THEN tests SHALL check error counts and types, not exact error message text
3. WHEN output format changes, THEN tests SHALL continue passing if behavior is correct
4. WHEN tests check for completion, THEN tests SHALL verify operation state, not presence of specific phrases
5. WHEN refactoring output formatting, THEN the system SHALL NOT require test changes unless behavior changes

### Requirement 4: Modular Error Handling

**User Story:** As a developer, I want error handling separated into clear modules, so that I can understand and modify error behavior without touching unrelated code.

#### Acceptance Criteria

1. WHEN an error occurs, THEN the system SHALL use the OperationError type to represent it
2. WHEN tracking file operations, THEN the system SHALL use FileOperationStats exclusively
3. WHEN tracking directory operations, THEN the system SHALL use DirectoryCleanupStats exclusively
4. WHEN combining results, THEN the system SHALL use OperationSummary to aggregate all statistics
5. WHEN adding new operation types, THEN the system SHALL extend the modular types, not add fields to a monolithic stats object

### Requirement 5: Clear Module Boundaries

**User Story:** As a developer, I want clear separation between file operations, directory operations, and result formatting, so that changes in one area don't break others.

#### Acceptance Criteria

1. WHEN the system moves files, THEN file move logic SHALL reside only in FolderOrganizer
2. WHEN the system formats results, THEN formatting logic SHALL reside only in result formatter modules
3. WHEN the system classifies files, THEN classification logic SHALL reside only in FileClassifier
4. WHEN the system removes directories, THEN directory removal logic SHALL be separate from file move logic
5. WHEN modules interact, THEN they SHALL use well-defined interfaces, not direct access to internal state

### Requirement 6: Backward Compatibility During Migration

**User Story:** As a developer, I want to migrate gradually without breaking existing functionality, so that I can refactor safely.

#### Acceptance Criteria

1. WHEN the refactor begins, THEN the system SHALL maintain both old and new result tracking temporarily
2. WHEN the CLI is updated, THEN the system SHALL use the new OperationSummary for display
3. WHEN tests are updated, THEN the system SHALL verify behavior using the new result types
4. WHEN the migration is complete, THEN the system SHALL remove all legacy OrganizationStats usage
5. WHEN the migration is complete, THEN all tests SHALL pass using only the new result types

### Requirement 7: Professional Code Quality Standards

**User Story:** As a developer, I want automated validation of code quality, so that the codebase maintains professional standards.

#### Acceptance Criteria

1. WHEN code is committed, THEN the system SHALL provide a single command to run all validations
2. WHEN validation runs, THEN the system SHALL check types with mypy
3. WHEN validation runs, THEN the system SHALL check style with ruff
4. WHEN validation runs, THEN the system SHALL run all tests with pytest
5. WHEN validation runs, THEN the system SHALL verify documentation completeness

### Requirement 8: Extensible Architecture

**User Story:** As a developer, I want to add new features without modifying existing code, so that the codebase follows open/closed principle.

#### Acceptance Criteria

1. WHEN adding a new operation type, THEN the system SHALL allow adding it via extension, not modification
2. WHEN adding a new error severity, THEN the system SHALL allow adding it to the ErrorSeverity enum
3. WHEN adding a new result formatter, THEN the system SHALL allow implementing a new formatter without changing existing ones
4. WHEN adding a new file category, THEN the system SHALL allow extending FileCategory without modifying FolderOrganizer
5. WHEN the architecture is complete, THEN the system SHALL document extension points for future developers
