  # Implementation Plan

- [x] 1. Create output formatting module with rich integration





  - Create `scrubb/output_formatter.py` with OutputFormatter class
  - Implement success, error, warning, and info message methods
  - Implement table creation for statistics display
  - Implement panel creation for grouped information
  - Implement file list printing with status indicators
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 1.1 Write property test for rich formatting presence


  - **Property 13: Rich formatting presence**
  - **Validates: Requirements 3.1, 3.3, 3.5**

- [x] 1.2 Write property test for path syntax highlighting


  - **Property 14: Path syntax highlighting**
  - **Validates: Requirements 3.4**

- [x] 2. Create prompt utilities module





  - Create `scrubb/prompt_utils.py` with PromptUtils class
  - Implement directory prompt with path validation
  - Implement confirmation prompt with multiple affirmative responses
  - Implement choice prompt with numbered options
  - Handle keyboard interrupts gracefully
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2.1 Write property test for path validation in prompts


  - **Property 17: Path validation in prompts**
  - **Validates: Requirements 5.1**

- [x] 2.2 Write property test for confirmation prompt acceptance


  - **Property 11: Confirmation prompt acceptance**
  - **Validates: Requirements 5.3, 8.3**


- [x] 2.3 Write property test for confirmation prompt rejection

  - **Property 12: Confirmation prompt rejection**
  - **Validates: Requirements 8.4**

- [x] 3. Create verbosity management module





  - Create `scrubb/verbosity.py` with VerbosityLevel enum and VerbosityManager class
  - Implement verbosity level checking methods
  - Implement context variable for global verbosity state
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 3.1 Write property test for quiet mode output suppression


  - **Property 7: Quiet mode output suppression**
  - **Validates: Requirements 7.2, 7.4**

- [x] 3.2 Write property test for verbose mode debug output



  - **Property 8: Verbose mode debug output**
  - **Validates: Requirements 7.1, 7.3**

- [x] 3.3 Write property test for default verbosity output


  - **Property 9: Default verbosity output**
  - **Validates: Requirements 7.5**

- [x] 4. Rename main command to emoji in CLI





  - Update `scrubb/cli.py` to rename `main` function to `emoji`
  - Update the `@app.command()` decorator to use name="emoji"
  - Update function docstring to reflect new command name
  - Update all internal references from main to emoji
  - _Requirements: 1.1, 2.1_

- [x] 4.1 Write property test for command name consistency


  - **Property 1: Command name consistency**
  - **Validates: Requirements 1.1**

- [x] 5. Add deprecation handler for main command





  - Create hidden `main` command that calls `emoji` command
  - Add deprecation warning using rich formatting
  - Log deprecation to stderr
  - _Requirements: 1.2_

- [x] 5.1 Write property test for deprecation warning display


  - **Property 2: Deprecation warning display**
  - **Validates: Requirements 1.2**

- [x] 6. Implement command aliases





  - Register `e` as alias for `emoji` command
  - Register `f` as alias for `folder` command
  - Register `s` as alias for `stats` command
  - Register `c` as alias for `config` command
  - Set `hidden=True` for alias commands to avoid cluttering help
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6.1 Write property test for command alias equivalence


  - **Property 6: Command alias equivalence**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 7. Add verbosity flags to all commands





  - Add `--verbose/-v` option to emoji command
  - Add `--quiet/-q` option to emoji command
  - Add `--verbose/-v` option to folder command
  - Add `--quiet/-q` option to folder command
  - Integrate VerbosityManager into command execution
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 8. Add auto-confirm flag to destructive operations





  - Add `--yes/-y` flag to stats reset command
  - Add `--yes/-y` flag to folder command
  - Implement confirmation prompt bypass logic
  - _Requirements: 8.5_

- [x] 8.1 Write property test for auto-confirm bypass


  - **Property 10: Auto-confirm bypass**
  - **Validates: Requirements 8.5**

- [x] 9. Add confirmation prompts to destructive operations





  - Add confirmation prompt to `stats --reset` command
  - Add confirmation prompt to `folder` command (when not in dry-run mode)
  - Use PromptUtils for confirmation prompts
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10. Enhance emoji statistics output





  - Update emoji output to show emoji character alongside codepoint count
  - Implement Unicode fallback for terminals without emoji support
  - Create formatted table for `stats --top` with rank, emoji, count, percentage
  - Add verbose mode emoji details (emoji, Unicode name, source file)
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 10.1 Write property test for emoji display format


  - **Property 18: Emoji display format**
  - **Validates: Requirements 9.1**

- [x] 10.2 Write property test for emoji statistics table format


  - **Property 19: Emoji statistics table format**
  - **Validates: Requirements 9.3**

- [x] 10.3 Write property test for verbose emoji details


  - **Property 20: Verbose emoji details**
  - **Validates: Requirements 9.4**

- [x] 11. Enhance error handling and messages





  - Update error display to use OutputFormatter
  - Add context and suggestions to all error messages
  - Include file paths in file operation errors
  - Implement error grouping for multiple errors
  - Add proper exit codes (1=general, 2=invalid input, 3=permission, 130=cancelled)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 10.3_

- [x] 11.1 Write property test for error message structure


  - **Property 15: Error message structure**
  - **Validates: Requirements 4.1, 4.2, 4.5**

- [x] 11.2 Write property test for file operation error details

  - **Property 16: File operation error details**
  - **Validates: Requirements 4.3**

- [x] 11.3 Write property test for error exit codes


  - **Property 21: Error exit codes**
  - **Validates: Requirements 10.3**

- [x] 12. Update COMMAND_REFERENCE.md documentation





  - Update command table to show `scrubb emoji` instead of `scrubb main`
  - Replace all command examples with new command name (currently shows "Main Command: scrubb main")
  - Add alias documentation for all commands (e, f, s, c)
  - Document verbosity flags (--verbose, --quiet) for all commands
  - Document confirmation prompts for destructive operations
  - Document auto-confirm flag (--yes) for stats and folder commands
  - _Requirements: 1.3, 2.3, 6.5, 7.1, 7.2, 8.1, 8.2, 8.5_

- [x] 13. Update README.md documentation





  - Update Quick Start section to mention command aliases
  - Add section documenting all command aliases (e, f, s, c)
  - Add section on verbosity modes (--verbose, --quiet) with examples
  - Add section on auto-confirm flag (--yes) with examples
  - Document confirmation prompts for destructive operations
  - Update usage examples to show alias usage
  - _Requirements: 1.3, 2.2, 6.5, 7.1, 7.2, 8.1, 8.2, 8.5_

- [x] 14. Checkpoint - Ensure all tests pass





  - Run full test suite to verify all implementations
  - Ensure all tests pass, ask the user if questions arise.
