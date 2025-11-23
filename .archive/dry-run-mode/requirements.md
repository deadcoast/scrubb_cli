# Requirements Document

## Introduction

This document specifies the requirements for adding a dry-run mode to the scrubb CLI tool's folder cleanup feature. The dry-run mode allows users to preview what changes would be made without actually executing them, providing detailed information about the planned operations. This helps users verify the cleanup behavior before committing to file system changes.

## Glossary

- **Dry-Run Mode**: A preview mode that simulates operations without making actual file system changes
- **Scrubb CLI**: The command-line tool for emoji scrubbing and file organization
- **Root Directory**: The user-specified directory path that will be analyzed
- **Scrubbed Folder**: A directory named "Scrubbed" that would be created in the root directory to store organized files
- **File Type Category**: A classification of files based on their extensions (Images, Video, Docs, Development)
- **Operation Plan**: A detailed list of actions that would be performed in a full run

## Requirements

### Requirement 1

**User Story:** As a user, I want to invoke dry-run mode with a flag, so that I can preview changes without modifying my file system.

#### Acceptance Criteria

1. WHEN a user executes `scrubb --folder --dry` THEN the system SHALL enter dry-run mode
2. WHEN dry-run mode is active THEN the system SHALL NOT create any directories
3. WHEN dry-run mode is active THEN the system SHALL NOT move any files
4. WHEN dry-run mode is active THEN the system SHALL NOT delete any directories
5. WHEN dry-run mode is active THEN the system SHALL analyze and report what would happen

### Requirement 2

**User Story:** As a user, I want to see which files would be moved and where, so that I can verify the categorization is correct.

#### Acceptance Criteria

1. WHEN dry-run mode completes THEN the system SHALL display a list of all files that would be moved
2. WHEN displaying file move operations THEN the system SHALL show the source path for each file
3. WHEN displaying file move operations THEN the system SHALL show the destination category for each file
4. WHEN displaying file move operations THEN the system SHALL group files by their target category
5. WHEN displaying file move operations THEN the system SHALL show the full destination path including any conflict resolution

### Requirement 3

**User Story:** As a user, I want to see detailed statistics about the planned operation, so that I understand the scope of changes.

#### Acceptance Criteria

1. WHEN dry-run mode completes THEN the system SHALL display the total number of files that would be moved
2. WHEN dry-run mode completes THEN the system SHALL display the count of files per category
3. WHEN dry-run mode completes THEN the system SHALL display the number of empty directories that would be removed
4. WHEN dry-run mode completes THEN the system SHALL display the list of directories that would be removed
5. WHEN dry-run mode completes THEN the system SHALL display the number of files that would be skipped due to unknown extensions

### Requirement 4

**User Story:** As a user, I want to see which files would encounter name conflicts, so that I can understand how conflicts will be resolved.

#### Acceptance Criteria

1. WHEN dry-run mode detects name conflicts THEN the system SHALL display a list of files that would be renamed
2. WHEN displaying conflict information THEN the system SHALL show the original filename
3. WHEN displaying conflict information THEN the system SHALL show the resolved filename with numeric suffix
4. WHEN displaying conflict information THEN the system SHALL group conflicts by category

### Requirement 5

**User Story:** As a user, I want to see which directories would be created, so that I understand the resulting folder structure.

#### Acceptance Criteria

1. WHEN dry-run mode completes THEN the system SHALL display a list of directories that would be created
2. WHEN displaying directory creation THEN the system SHALL show the full path of each new directory
3. WHEN the Scrubbed folder would be created THEN the system SHALL indicate this in the output
4. WHEN category subdirectories would be created THEN the system SHALL list each one

### Requirement 6

**User Story:** As a user, I want to see files that would be skipped, so that I know which files won't be organized.

#### Acceptance Criteria

1. WHEN dry-run mode encounters files with unknown extensions THEN the system SHALL list these files
2. WHEN displaying skipped files THEN the system SHALL show the file path
3. WHEN displaying skipped files THEN the system SHALL show the reason for skipping
4. WHEN no files would be skipped THEN the system SHALL indicate that all files would be processed

### Requirement 7

**User Story:** As a user, I want clear visual distinction between dry-run and actual execution, so that I don't confuse preview with actual changes.

#### Acceptance Criteria

1. WHEN dry-run mode starts THEN the system SHALL display a prominent message indicating dry-run mode is active
2. WHEN dry-run mode completes THEN the system SHALL display a message reminding the user no changes were made
3. WHEN displaying operations THEN the system SHALL use language indicating future actions (would move, would create, would remove)
4. WHEN dry-run mode is active THEN the system SHALL use distinct visual formatting or colors to differentiate from actual execution

### Requirement 8

**User Story:** As a user, I want to see potential errors that might occur, so that I can address issues before running the actual operation.

#### Acceptance Criteria

1. WHEN dry-run mode detects files that might be inaccessible THEN the system SHALL list potential permission issues
2. WHEN dry-run mode detects insufficient disk space indicators THEN the system SHALL warn about potential space issues
3. WHEN dry-run mode completes THEN the system SHALL display a count of potential errors
4. WHEN no potential errors are detected THEN the system SHALL indicate the operation should proceed smoothly

### Requirement 9

**User Story:** As a user, I want the dry-run output to be well-organized and readable, so that I can easily review the planned changes.

#### Acceptance Criteria

1. WHEN dry-run mode displays output THEN the system SHALL organize information into clear sections
2. WHEN dry-run mode displays output THEN the system SHALL use headers to separate different types of information
3. WHEN dry-run mode displays lists THEN the system SHALL format them for easy scanning
4. WHEN dry-run mode displays paths THEN the system SHALL use consistent formatting throughout

### Requirement 10

**User Story:** As a developer, I want the dry-run mode to reuse existing logic, so that the preview accurately reflects actual behavior.

#### Acceptance Criteria

1. WHEN dry-run mode analyzes files THEN the system SHALL use the same classification logic as the actual operation
2. WHEN dry-run mode detects conflicts THEN the system SHALL use the same conflict resolution logic as the actual operation
3. WHEN dry-run mode identifies empty directories THEN the system SHALL use the same detection logic as the actual operation
4. WHEN dry-run mode completes THEN the system SHALL produce results that match what would happen in actual execution
