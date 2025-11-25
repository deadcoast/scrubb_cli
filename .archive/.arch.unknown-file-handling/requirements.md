# Requirements Document

## Introduction

The Scrubb file organization tool currently skips files with unknown extensions, leaving them unorganized. Additionally, the folder organization command may have integration issues that prevent it from executing properly. This feature will ensure all files are organized by creating a dedicated category for files with unrecognized extensions, and verify that the entire folder organization pipeline works correctly from CLI to file system operations.

## Glossary

- **Scrubb**: The file organization tool that categorizes and moves files into organized folders
- **FileClassifier**: The component that determines which category a file belongs to based on its extension
- **FolderOrganizer**: The component that moves files into their categorized folders
- **Unknown Extension**: A file extension that is not recognized by any of the predefined category mappings
- **FileCategory**: An enumeration representing the different categories files can be organized into
- **CLI**: Command-line interface that provides user interaction with the folder organization functionality
- **Scrubbed Folder**: The destination folder where organized files are moved, containing category subfolders

## Requirements

### Requirement 1

**User Story:** As a user organizing my files, I want files with unknown extensions to be moved to a dedicated folder, so that all files are organized and none are left behind.

#### Acceptance Criteria

1. WHEN the FileClassifier encounters a file with an unknown extension, THEN the system SHALL assign it to an "Other" category
2. WHEN the FolderOrganizer processes files with the "Other" category, THEN the system SHALL move them to a folder named "Other"
3. WHEN organizing files in dry-run mode, THEN the system SHALL include unknown extension files in the preview with their "Other" category destination
4. WHEN organizing files in actual mode, THEN the system SHALL move unknown extension files to the "Other" folder alongside other categorized files
5. WHEN displaying statistics, THEN the system SHALL include the count of files moved to the "Other" category

### Requirement 2

**User Story:** As a user, I want to see which files have unknown extensions in the dry-run preview, so that I can understand what will be categorized as "Other".

#### Acceptance Criteria

1. WHEN running in dry-run mode, THEN the system SHALL display files with unknown extensions under the "Other" category in the file operations section
2. WHEN displaying dry-run statistics, THEN the system SHALL show the count of files in the "Other" category in the files by category section
3. WHEN a file has no extension, THEN the system SHALL treat it as an unknown extension and assign it to the "Other" category

### Requirement 3

**User Story:** As a user running the folder command, I want the system to execute successfully and provide feedback, so that I know the operation is working correctly.

#### Acceptance Criteria

1. WHEN the folder command is invoked, THEN the system SHALL prompt for a directory path
2. WHEN a valid directory path is provided, THEN the system SHALL scan the directory for files
3. WHEN files are found in the directory, THEN the system SHALL categorize and process each file
4. WHEN the organization completes, THEN the system SHALL display statistics showing files moved by category
5. WHEN no files are found or all files are already organized, THEN the system SHALL display a message indicating no changes were made

### Requirement 4

**User Story:** As a developer debugging the folder organization feature, I want comprehensive logging and error handling, so that I can identify where failures occur in the pipeline.

#### Acceptance Criteria

1. WHEN the folder command starts execution, THEN the system SHALL log the target directory being processed
2. WHEN files are being scanned, THEN the system SHALL log the number of files discovered
3. WHEN files are being categorized, THEN the system SHALL log each category assignment in verbose mode
4. WHEN errors occur during file operations, THEN the system SHALL capture and display specific error messages with file paths
5. WHEN the operation completes, THEN the system SHALL display a summary of all operations performed
