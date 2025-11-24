# Architecture

This document describes the system architecture and design of scrubb, a multi-function CLI tool for emoji scrubbing and folder cleanup.

## Overview

scrubb is designed as a modular, command-line application with clear separation of concerns. The architecture follows a layered approach with distinct components for CLI interaction, business logic, file system operations, and data persistence.

### Design Principles

- **Modularity**: Each component has a single, well-defined responsibility
- **Testability**: Components are designed to be easily testable with both unit and property-based tests
- **Safety**: Operations include dry-run modes and validation to prevent data loss
- **Cross-Platform**: Platform-agnostic design with proper path handling and XDG compliance
- **User Experience**: Rich terminal output with progress indicators and detailed statistics

## System Architecture

```

                        CLI Layer                             
                        (cli.py)                              
  - Command parsing and routing                               
  - User input/output                                         
  - Error handling and display                                

                            
                            

                    Business Logic Layer                      

  Emoji Scrubbing            Folder Cleanup                  
  - scrubber.py              - folder_organizer.py           
  - ignore.py                - file_classifier.py            
                             - directory_scanner.py          
                             - tree_visualizer.py            
                             - tree_renderer.py              
                             - tree_comparator.py            
                             - statistics_calculator.py      

                            
                            

                   Infrastructure Layer                       
  - config.py (Configuration & XDG paths)                     
  - tree_models.py (Data models)                              
  - File system operations                                    
  - Statistics persistence                                    

```

## Core Components

### CLI Layer

#### cli.py
**Purpose**: Command-line interface and user interaction

**Responsibilities**:
- Parse command-line arguments using Typer
- Route commands to appropriate handlers
- Display results and statistics using Rich
- Handle user prompts and confirmations
- Format error messages and help text

**Key Commands**:
- `scrubb [PATH] [EXECUTOR]` - Emoji scrubbing
- `scrubb folder [--dry] [--tree]` - Folder cleanup
- `scrubb stats [--top] [--reset]` - Statistics management
- `scrubb config` - Configuration management

### Business Logic Layer

#### Emoji Scrubbing Components

##### scrubber.py
**Purpose**: Core emoji detection and removal logic

**Responsibilities**:
- Detect emojis using comprehensive Unicode regex patterns
- Remove emoji sequences from text while preserving structure
- Track per-run statistics (files processed, emojis removed)
- Update persistent global statistics
- Manage statistics file persistence

**Key Features**:
- Unicode range coverage: emoticons, symbols, flags, dingbats, etc.
- Per-emoji token counting
- Safe file modification (only writes if emojis found)

##### ignore.py
**Purpose**: File and directory filtering

**Responsibilities**:
- Match files against ignore patterns
- Support glob-style pattern matching
- Provide default ignore patterns for common directories
- Filter by file extension

**Default Ignore Patterns**:
- Build artifacts: `.venv`, `__pycache__`, `node_modules`
- Version control: `.git`, `.svn`
- IDE files: `.vscode`, `.idea`
- Binary files: `*.pyc`, `*.exe`, `*.dll`
- Archives: `*.zip`, `*.tar.gz`

#### Folder Cleanup Components

##### folder_organizer.py
**Purpose**: Orchestrate folder cleanup operations

**Responsibilities**:
- Scan directories recursively
- Categorize files using file_classifier
- Move files to organized structure
- Handle filename conflicts with incremental numbering
- Remove empty directories
- Generate operation statistics
- Support dry-run mode for preview

**Organization Structure**:
```
Scrubbed/
 Images/
 Video/
 Docs/
    Markdown/
    Other Docs/
 Development/
```

##### file_classifier.py
**Purpose**: Classify files by type based on extension

**Responsibilities**:
- Map file extensions to categories
- Determine target directory for each file type
- Support extensible category system

**Categories**:
- **Images**: jpg, png, gif, svg, webp, etc.
- **Video**: mp4, avi, mov, mkv, etc.
- **Markdown**: md, markdown
- **Other Docs**: pdf, doc, txt, xlsx, etc.
- **Development**: py, js, ts, java, c, cpp, etc.

##### directory_scanner.py
**Purpose**: Scan and analyze directory structures

**Responsibilities**:
- Recursively traverse directory trees
- Collect file and directory information
- Calculate directory statistics (size, depth, file counts)
- Build tree data models
- Handle permission errors gracefully

##### tree_visualizer.py
**Purpose**: Generate visual directory tree representations

**Responsibilities**:
- Create before/after tree visualizations
- Simulate post-cleanup directory structure
- Coordinate tree rendering and comparison
- Display comprehensive statistics

##### tree_renderer.py
**Purpose**: Render directory trees as formatted text

**Responsibilities**:
- Format tree structures with box-drawing characters
- Color-code files by category
- Generate clean, readable tree output
- Handle deep nesting gracefully

##### tree_comparator.py
**Purpose**: Compare before and after directory states

**Responsibilities**:
- Calculate differences between tree states
- Track changes in file counts, directory counts, sizes
- Generate comparison statistics
- Format comparison output

##### statistics_calculator.py
**Purpose**: Calculate directory and file statistics

**Responsibilities**:
- Count files and directories
- Calculate total sizes
- Determine maximum depth
- Categorize files by type
- Aggregate statistics across trees

##### tree_models.py
**Purpose**: Data models for tree structures

**Key Models**:
- `TreeNode`: Represents a file or directory in the tree
- `TreeStatistics`: Statistics for a directory tree
- `ComparisonResult`: Before/after comparison data

### Infrastructure Layer

#### config.py
**Purpose**: Configuration management and persistence

**Responsibilities**:
- Manage user configuration (default root path, ignore patterns)
- Implement XDG Base Directory specification
- Provide platform-specific paths (Windows, macOS, Linux)
- Load and save configuration files
- Manage statistics file location

**File Locations**:
- Config: `~/.config/scrubb/config.json` (XDG_CONFIG_HOME)
- Stats: `~/.local/state/scrubb/stats.json` (XDG_STATE_HOME)
- Windows: Uses `%APPDATA%` and `%LOCALAPPDATA%`

## Data Flow

### Emoji Scrubbing Flow

```
User Command
    
    
CLI Parser (cli.py)
    
    
Path Resolution (config.py)
    
    
File Discovery & Filtering (ignore.py)
    
    
Emoji Detection & Removal (scrubber.py)
    
    
Statistics Update (scrubber.py)
    
    
Results Display (cli.py)
```

### Folder Cleanup Flow

```
User Command
    
    
CLI Parser (cli.py)
    
    
Directory Scanning (directory_scanner.py)
    
     Tree Visualization (tree_visualizer.py)
        Tree Rendering (tree_renderer.py)
    
    
File Classification (file_classifier.py)
    
    
Dry-Run Check
    
     [Dry-Run] Simulate & Display
    
     [Execute] File Organization (folder_organizer.py)
            
             Move Files
             Handle Conflicts
             Remove Empty Directories
                
                
            Statistics Calculation (statistics_calculator.py)
                
                
            Tree Comparison (tree_comparator.py)
                
                
            Results Display (cli.py)
```

## Design Patterns

### Strategy Pattern
Used in file classification where different file types are categorized based on extension patterns.

### Command Pattern
CLI commands are encapsulated as separate functions with clear interfaces.

### Builder Pattern
Tree structures are built incrementally during directory scanning.

### Template Method
Statistics calculation follows a template with customizable aggregation steps.

## Error Handling

### Graceful Degradation
- Permission errors during scanning are logged but don't stop processing
- Unrecognized file types are skipped rather than causing failures
- Invalid paths are validated before operations begin

### Dry-Run Safety
- All destructive operations support dry-run mode
- Dry-run mode performs full validation without file system changes
- Users can preview all operations before committing

### Validation
- Path existence validation before processing
- File type validation before operations
- Configuration validation on load
- Statistics file integrity checks

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock file system operations where appropriate
- Verify business logic correctness
- Test edge cases and error conditions

### Property-Based Tests
- Use Hypothesis for property-based testing
- Verify invariants across random inputs
- Test file content preservation
- Verify tree structure properties
- Validate statistics calculations

### Integration Tests
- Test complete workflows end-to-end
- Verify component interactions
- Test with real file system operations
- Validate cross-platform behavior

## Performance Considerations

### File System Operations
- Minimize redundant file system calls
- Use efficient directory traversal
- Batch operations where possible
- Cache file metadata during scanning

### Memory Management
- Stream large files rather than loading entirely
- Use generators for directory traversal
- Clean up resources promptly
- Avoid unnecessary data duplication

### Scalability
- Handle large directory trees efficiently
- Support deep nesting without stack overflow
- Process thousands of files without performance degradation
- Maintain responsive CLI even with large operations

## Security Considerations

### Path Traversal Prevention
- Validate all user-provided paths
- Prevent access outside intended directories
- Sanitize file paths before operations

### Safe File Operations
- Verify write permissions before modifications
- Use atomic operations where possible
- Preserve file permissions and attributes
- Handle symbolic links safely

### Data Privacy
- No external network calls
- All data stored locally
- No telemetry or tracking
- User configuration remains private

## Future Extensibility

### Plugin System
The architecture supports future plugin systems for:
- Custom file classifiers
- Additional organization strategies
- Custom statistics collectors
- Alternative output formats

### Configuration Extensions
- User-defined file categories
- Custom ignore patterns
- Configurable organization structures
- Theme customization for tree output

### API Layer
The modular design allows for future API exposure:
- Programmatic access to scrubbing logic
- Library usage in other Python projects
- Integration with other tools

## Dependencies

### Core Dependencies
- **typer**: CLI framework with type hints and automatic help generation
- **rich**: Terminal formatting, colors, and progress indicators

### Development Dependencies
- **pytest**: Testing framework
- **hypothesis**: Property-based testing
- **coverage**: Code coverage analysis

### Platform Dependencies
- Python 3.10+ for modern type hints and pattern matching
- Cross-platform file system support
- XDG Base Directory specification (Linux/macOS)

## Conclusion

The scrubb architecture prioritizes modularity, testability, and user safety. Each component has clear responsibilities and well-defined interfaces, making the codebase maintainable and extensible. The layered design separates concerns effectively, while the comprehensive testing strategy ensures reliability across platforms and use cases.
