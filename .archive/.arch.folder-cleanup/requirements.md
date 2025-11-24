# Requirements Document

## Introduction

This document specifies the requirements for adding a folder cleanup feature to the scrubb CLI tool. The feature will organize files into categorized folders and remove empty directories. This extends scrubb's capabilities beyond emoji scrubbing to include file organization functionality.

## Glossary

- **Scrubb CLI**: The command-line tool for emoji scrubbing and file organization
- **Root Directory**: The user-specified directory path that will be recursively searched and cleaned
- **Scrubbed Folder**: A directory named "Scrubbed" created in the root directory to store organized files
- **Empty Folder**: A directory containing no files or subdirectories
- **File Type Category**: A classification of files based on their extensions (Images, Video, Docs, Development)
- **Recursive Search**: The process of traversing all subdirectories within a directory tree

## Requirements

### Requirement 1

**User Story:** As a user, I want to invoke folder cleanup functionality via a command-line flag, so that I can organize my files without affecting the emoji scrubbing feature.

#### Acceptance Criteria

1. WHEN a user executes `scrubb --folder` THEN the system SHALL prompt for a directory path
2. WHEN the folder cleanup command is invoked THEN the system SHALL NOT execute emoji scrubbing functionality
3. WHEN a user provides the `--folder` flag THEN the system SHALL enter folder cleanup mode exclusively

### Requirement 2

**User Story:** As a user, I want to specify which directory to clean up, so that I can organize files in any location on my system.

#### Acceptance Criteria

1. WHEN the system prompts for a directory path THEN the system SHALL accept both absolute and relative paths
2. WHEN a user provides a non-existent directory path THEN the system SHALL display an error message and exit gracefully
3. WHEN a user provides a valid directory path THEN the system SHALL use that path as the root directory for cleanup operations
4. WHEN a user provides a path with tilde expansion THEN the system SHALL resolve the path correctly

### Requirement 3

**User Story:** As a user, I want my files automatically categorized and moved to organized folders, so that I can easily locate files by type.

#### Acceptance Criteria

1. WHEN the system processes image files THEN the system SHALL move them to "Scrubbed/Images/"
2. WHEN the system processes video files THEN the system SHALL move them to "Scrubbed/Video/"
3. WHEN the system processes markdown files THEN the system SHALL move them to "Scrubbed/Docs/Markdown/"
4. WHEN the system processes non-markdown document files THEN the system SHALL move them to "Scrubbed/Docs/Other Docs/"
5. WHEN the system processes code files THEN the system SHALL move them to "Scrubbed/Development/"
6. WHERE the Scrubbed folder does not exist THEN the system SHALL create it in the root directory
7. WHERE category subdirectories do not exist THEN the system SHALL create them as needed

### Requirement 4

**User Story:** As a user, I want the system to handle file name conflicts, so that no files are lost during the organization process.

#### Acceptance Criteria

1. WHEN a file with the same name exists in the destination folder THEN the system SHALL rename the incoming file with a numeric suffix
2. WHEN multiple files with the same name are moved THEN the system SHALL append incrementing numbers to preserve all files
3. WHEN renaming files THEN the system SHALL preserve the original file extension

### Requirement 5

**User Story:** As a user, I want empty folders removed after file organization, so that my directory structure remains clean.

#### Acceptance Criteria

1. WHEN all files have been moved from a directory THEN the system SHALL remove that empty directory
2. WHEN a directory contains only empty subdirectories THEN the system SHALL remove all empty subdirectories recursively
3. WHEN the cleanup process completes THEN the system SHALL remove empty folders as the final step
4. WHEN the root directory becomes empty THEN the system SHALL NOT remove the root directory itself
5. WHEN the Scrubbed folder or its subdirectories are empty THEN the system SHALL NOT remove them

### Requirement 6

**User Story:** As a user, I want to see statistics about the cleanup operation, so that I understand what changes were made.

#### Acceptance Criteria

1. WHEN the cleanup operation completes THEN the system SHALL display the total number of files moved
2. WHEN the cleanup operation completes THEN the system SHALL display the number of files moved per category
3. WHEN the cleanup operation completes THEN the system SHALL display the number of empty folders removed
4. WHEN errors occur during processing THEN the system SHALL display the number of errors encountered

### Requirement 7

**User Story:** As a user, I want the system to recursively search all subdirectories, so that all files in the directory tree are organized.

#### Acceptance Criteria

1. WHEN the system processes the root directory THEN the system SHALL traverse all subdirectories recursively
2. WHEN the system encounters nested directories THEN the system SHALL process files at all depth levels
3. WHEN the system moves files THEN the system SHALL NOT preserve the original directory structure in the destination

### Requirement 8

**User Story:** As a developer, I want clear file type definitions for each category, so that the system correctly classifies files.

#### Acceptance Criteria

1. WHEN classifying files THEN the system SHALL recognize common image extensions including .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff
2. WHEN classifying files THEN the system SHALL recognize common video extensions including .mp4, .avi, .mov, .mkv, .flv, .wmv, .webm, .m4v, .mpeg
3. WHEN classifying files THEN the system SHALL recognize markdown extensions including .md and .markdown
4. WHEN classifying files THEN the system SHALL recognize document extensions including .pdf, .doc, .docx, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx, .csv
5. WHEN classifying files THEN the system SHALL recognize code file extensions including .py, .js, .ts, .java, .c, .cpp, .h, .rs, .go, .rb, .php, .html, .css, .json, .xml, .yaml, .yml, .toml, .sh, .bash
6. WHEN a file has no extension or an unrecognized extension THEN the system SHALL skip that file

### Requirement 9

**User Story:** As a user, I want the system to handle errors gracefully, so that the cleanup process continues even if individual files fail.

#### Acceptance Criteria

1. WHEN a file cannot be moved due to permissions THEN the system SHALL log the error and continue processing other files
2. WHEN a file cannot be accessed THEN the system SHALL increment the error counter and continue processing
3. WHEN the cleanup operation encounters errors THEN the system SHALL complete the operation and report all errors at the end
