# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-24

### Added

#### Emoji Scrubbing
- Smart emoji detection across comprehensive Unicode ranges (emoticons, symbols, flags, etc.)
- Persistent global statistics tracking with per-emoji breakdowns
- Configurable ignore patterns for common directories and file types
- Safe file processing with recognized text extension filtering
- Per-run ephemeral statistics display
- Statistics viewing with `scrubb stats` command
- Top emoji tokens display with `scrubb stats --top`
- Statistics reset capability with `scrubb stats --reset`

#### Folder Cleanup
- Automatic file categorization by type (Images, Video, Documents, Development)
- Tree visualization with before/after directory structures using `--tree` flag
- Dry-run mode for safe preview of all changes with `--dry` flag
- Smart conflict resolution with incremental numbering for duplicate filenames
- Empty folder removal including hidden system files (`.DS_Store`, `Thumbs.db`)
- Recursive directory processing at all depths
- Detailed statistics reporting (files moved, categories used, folders removed)
- Five file categories: Images, Video, Markdown Docs, Other Docs, Development

#### General Features
- Cross-platform support (Windows, macOS, Linux)
- XDG Base Directory specification compliance
- Flexible path resolution (relative, absolute, subdirectory)
- Configuration management with `scrubb config` command
- Default root directory configuration
- Comprehensive ignore patterns for build artifacts and system files

#### Developer Features
- UV ecosystem integration for fast package management
- Comprehensive test suite with 71+ tests
- Property-based testing with Hypothesis
- Unit tests for all core components
- Integration tests for end-to-end workflows
- Development mode installation support

### Technical Details

#### Core Components
- `cli.py` - Typer-based CLI entrypoint and command definitions
- `config.py` - Configuration management with XDG path support
- `ignore.py` - File ignore pattern matching
- `scrubber.py` - Emoji removal logic and statistics tracking
- `file_classifier.py` - File type classification system
- `folder_organizer.py` - Folder organization and cleanup logic
- `directory_scanner.py` - Directory tree scanning and analysis
- `tree_visualizer.py` - Tree visualization and rendering
- `tree_renderer.py` - Tree formatting and display
- `tree_comparator.py` - Before/after tree comparison
- `statistics_calculator.py` - Statistics calculation and aggregation
- `tree_models.py` - Data models for tree structures

#### Dependencies
- Python 3.10+
- typer >= 0.12.3
- rich >= 13.0.0

### Documentation
- Command reference guide
- Architecture documentation
- Contributing guidelines
- Development documentation

[0.1.0]: https://github.com/yourusername/scrubb/releases/tag/v0.1.0
