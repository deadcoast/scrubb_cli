# Requirements Document

## Introduction

This specification addresses two key improvements to the scrubb CLI tool:
1. Renaming the problematic `main` command to `emoji` for better clarity and consistency
2. Introducing enhancements and third-party libraries to improve the CLI design and user experience

The `main` command name is problematic because it conflicts with common programming conventions where "main" typically refers to entry points, making the CLI less intuitive. The new `emoji` command name clearly indicates its purpose: emoji scrubbing operations.

## Glossary

- **CLI**: Command-Line Interface - the text-based interface for interacting with scrubb
- **scrubb**: The emoji scrubber and file organization tool
- **emoji command**: The renamed command (formerly `main`) that removes emojis from text files
- **typer**: The Python CLI framework used by scrubb
- **rich**: A Python library for rich text and beautiful formatting in the terminal
- **click**: The underlying framework that typer is built upon
- **XDG**: X Desktop Group - standards for configuration file locations on Unix-like systems

## Requirements

### Requirement 1

**User Story:** As a CLI user, I want the emoji scrubbing command to be named `emoji` instead of `main`, so that the command name clearly indicates its purpose and doesn't conflict with common programming conventions.

#### Acceptance Criteria

1. WHEN a user runs `scrubb emoji [PATH] .` THEN the system SHALL execute emoji scrubbing operations with the same functionality as the former `main` command
2. WHEN a user runs `scrubb main [PATH] .` THEN the system SHALL display a deprecation warning and redirect to the `emoji` command
3. WHEN documentation references the emoji scrubbing command THEN the system SHALL use `scrubb emoji` instead of `scrubb main`
4. WHEN help text is displayed THEN the system SHALL show `emoji` as the command name for emoji scrubbing operations
5. WHEN test files reference the emoji scrubbing command THEN the system SHALL use the `emoji` command name

### Requirement 2

**User Story:** As a developer maintaining the codebase, I want all references to the `main` command updated across the entire ecosystem, so that the codebase is consistent and maintainable.

#### Acceptance Criteria

1. WHEN the CLI module defines commands THEN the system SHALL register the emoji scrubbing function with the name `emoji`
2. WHEN the README documentation describes commands THEN the system SHALL reference `scrubb emoji` for emoji scrubbing operations
3. WHEN the COMMAND_REFERENCE documentation lists commands THEN the system SHALL show `scrubb emoji` in all command tables and examples
4. WHEN test files invoke the emoji scrubbing command THEN the system SHALL use `scrubb emoji` in test invocations
5. WHEN example scripts demonstrate usage THEN the system SHALL use `scrubb emoji` in code examples

### Requirement 3

**User Story:** As a CLI user, I want enhanced visual feedback and formatting, so that I can better understand command output and navigate the interface.

#### Acceptance Criteria

1. WHEN the system displays command output THEN the system SHALL use rich formatting for improved readability
2. WHEN the system shows progress for long operations THEN the system SHALL display a progress bar with percentage and time estimates
3. WHEN the system displays tables of information THEN the system SHALL use formatted tables with proper alignment and borders
4. WHEN the system shows file paths THEN the system SHALL use syntax highlighting to distinguish different path components
5. WHEN the system displays statistics THEN the system SHALL use visual panels with clear section separation

### Requirement 4

**User Story:** As a CLI user, I want improved error messages and validation, so that I can quickly understand and fix issues.

#### Acceptance Criteria

1. WHEN the system encounters an error THEN the system SHALL display a formatted error message with context and suggested solutions
2. WHEN a user provides invalid input THEN the system SHALL show clear validation messages with examples of valid input
3. WHEN a file operation fails THEN the system SHALL display the specific file path and reason for failure
4. WHEN multiple errors occur THEN the system SHALL group and summarize errors by type
5. WHEN the system suggests corrections THEN the system SHALL highlight the suggested command or path

### Requirement 5

**User Story:** As a CLI user, I want interactive prompts with validation, so that I can provide input safely and receive immediate feedback.

#### Acceptance Criteria

1. WHEN the system prompts for a directory path THEN the system SHALL validate the path exists before proceeding
2. WHEN a user provides invalid input to a prompt THEN the system SHALL display an error and re-prompt without exiting
3. WHEN the system prompts for confirmation THEN the system SHALL accept common affirmative responses (yes, y, Y, YES)
4. WHEN a prompt has a default value THEN the system SHALL display the default clearly and allow the user to accept it by pressing Enter
5. WHEN the system prompts for a choice THEN the system SHALL display numbered options and accept numeric input

### Requirement 6

**User Story:** As a CLI user, I want command aliases and shortcuts, so that I can work more efficiently with frequently used commands.

#### Acceptance Criteria

1. WHEN a user runs `scrubb e` THEN the system SHALL recognize it as an alias for `scrubb emoji`
2. WHEN a user runs `scrubb f` THEN the system SHALL recognize it as an alias for `scrubb folder`
3. WHEN a user runs `scrubb s` THEN the system SHALL recognize it as an alias for `scrubb stats`
4. WHEN a user runs `scrubb c` THEN the system SHALL recognize it as an alias for `scrubb config`
5. WHEN help text is displayed THEN the system SHALL show available aliases for each command

### Requirement 7

**User Story:** As a CLI user, I want verbose and quiet modes, so that I can control the amount of output based on my needs.

#### Acceptance Criteria

1. WHEN a user runs a command with `--verbose` or `-v` THEN the system SHALL display detailed debug information including file-by-file processing
2. WHEN a user runs a command with `--quiet` or `-q` THEN the system SHALL suppress all non-essential output and only show errors
3. WHEN verbose mode is enabled THEN the system SHALL log timestamps for each operation
4. WHEN quiet mode is enabled THEN the system SHALL still display critical errors and warnings
5. WHEN neither verbose nor quiet mode is specified THEN the system SHALL display standard output with summary statistics

### Requirement 8

**User Story:** As a CLI user, I want confirmation prompts for destructive operations, so that I can prevent accidental data loss.

#### Acceptance Criteria

1. WHEN a user runs `scrubb stats --reset` THEN the system SHALL prompt for confirmation before clearing statistics
2. WHEN a user runs `scrubb folder` without `--dry` THEN the system SHALL display a summary and prompt for confirmation before moving files
3. WHEN a confirmation prompt is displayed THEN the system SHALL accept 'yes', 'y', or Enter to proceed
4. WHEN a user responds negatively to a confirmation THEN the system SHALL cancel the operation and exit gracefully
5. WHEN a user runs a command with `--yes` or `-y` flag THEN the system SHALL skip confirmation prompts and proceed automatically

### Requirement 9

**User Story:** As a CLI user, I want better output formatting for emoji statistics, so that I can see which emojis were removed with proper visual representation.

#### Acceptance Criteria

1. WHEN the system displays removed emoji tokens THEN the system SHALL show the actual emoji character alongside the codepoint count
2. WHEN emoji characters cannot be displayed in the terminal THEN the system SHALL fall back to Unicode codepoint notation
3. WHEN displaying top emoji statistics THEN the system SHALL use a formatted table with columns for rank, emoji, count, and percentage
4. WHEN showing emoji removal in verbose mode THEN the system SHALL display the emoji, its Unicode name, and the file where it was found
5. WHEN the terminal supports Unicode THEN the system SHALL display emojis in color when possible

### Requirement 10

**User Story:** As a developer, I want the CLI to use modern Python CLI best practices, so that the tool is maintainable and follows industry standards.

#### Acceptance Criteria

1. WHEN the CLI is invoked THEN the system SHALL use typer's modern parameter syntax with proper type hints
2. WHEN commands are defined THEN the system SHALL use typer's callback decorators for shared options
3. WHEN the CLI handles errors THEN the system SHALL use proper exception handling with appropriate exit codes
4. WHEN the CLI displays help THEN the system SHALL use typer's rich integration for formatted help text
5. WHEN the CLI processes arguments THEN the system SHALL validate inputs using typer's validation features
