# Implementation Plan

- [x] 1. Set up project dependencies and module structure





  - Add `rich>=13.0.0` to pyproject.toml dependencies
  - Create `scrubb/tree_visualizer.py` module file
  - Create `scrubb/tree_renderer.py` module file
  - Create `scrubb/directory_scanner.py` module file
  - Create `scrubb/statistics_calculator.py` module file
  - Create `scrubb/tree_comparator.py` module file
  - _Requirements: 10.1, 10.4_

- [x] 2. Implement core data models





  - [x] 2.1 Create DirectoryNode dataclass


    - Define DirectoryNode with path, name, is_directory, size, children, category, depth, is_new, is_removed fields
    - Implement __post_init__ for validation
    - _Requirements: 4.2, 4.3, 5.2_
  
  - [x] 2.2 Create DirectoryStatistics dataclass


    - Define DirectoryStatistics with total_files, total_directories, total_size, max_depth, files_by_category, size_by_category fields
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 2.3 Create StatisticsDelta dataclass


    - Define StatisticsDelta with files_delta, directories_delta, size_delta, depth_delta, category_deltas fields
    - Implement format_delta_value method for +/- formatting
    - _Requirements: 6.2, 6.3, 6.4, 6.5_
  
  - [x] 2.4 Create DirectorySnapshot dataclass


    - Define DirectorySnapshot with root_path, root_node, statistics, timestamp, is_simulated fields
    - _Requirements: 1.3, 1.4_

- [x] 3. Implement StatisticsCalculator





  - [x] 3.1 Implement calculate method


    - Traverse DirectoryNode tree to count files and directories
    - Calculate total size by summing file sizes
    - Determine maximum depth from node depths
    - Categorize files using FileClassifier
    - Build files_by_category and size_by_category dictionaries
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 3.2 Write property test for statistics calculation


    - **Property 2: Statistics calculation correctness**
    - **Validates: Requirements 2.1, 2.5**
  
  - [x] 3.3 Implement calculate_delta method


    - Calculate differences between before and after statistics
    - Return StatisticsDelta with all delta values
    - _Requirements: 6.2, 6.3, 6.4_
  
  - [x] 3.4 Write property test for delta calculation

    - **Property 3: Delta calculation symmetry**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5**
  
  - [x] 3.5 Implement format_size static method

    - Convert bytes to human-readable format (B, KB, MB, GB, TB)
    - Use 1024 as conversion factor
    - _Requirements: 2.4_

- [x] 4. Implement DirectoryScanner





  - [x] 4.1 Implement scan method


    - Accept root_path as parameter
    - Call _traverse to build directory tree
    - Call StatisticsCalculator.calculate to get statistics
    - Return DirectorySnapshot with current timestamp
    - _Requirements: 1.3, 1.4, 4.2, 4.3_
  
  - [x] 4.2 Implement _traverse recursive method


    - Accept path and depth parameters
    - Create DirectoryNode for current path
    - If directory, recursively traverse children
    - If file, get size and classify using FileClassifier
    - Track depth for each node
    - Handle permission errors gracefully
    - _Requirements: 4.2, 4.3, 7.1, 12.4_
  
  - [x] 4.3 Write property test for tree capture consistency


    - **Property 1: Tree capture consistency**
    - **Validates: Requirements 1.3, 1.4**
  
  - [x] 4.4 Write property test for directory count accuracy

    - **Property 7: Directory count accuracy**
    - **Validates: Requirements 2.2**
  
  - [x] 4.5 Write property test for depth calculation

    - **Property 8: Depth calculation correctness**
    - **Validates: Requirements 2.3**
  
  - [x] 4.6 Write property test for size calculation

    - **Property 9: Size calculation consistency**
    - **Validates: Requirements 2.4**

- [x] 5. Implement TreeRenderer with rich library





  - [x] 5.1 Implement __init__ with configuration

    - Accept max_depth and max_files_per_dir parameters
    - Initialize rich Console
    - Check if rich library is available
    - _Requirements: 3.1, 8.3, 8.4_
  
  - [x] 5.2 Implement render method


    - Accept DirectorySnapshot and title parameters
    - Create rich Tree with title
    - Call _build_tree to populate tree structure
    - Print tree using Console
    - Handle rendering errors gracefully
    - _Requirements: 3.2, 4.1, 5.1, 12.1_
  
  - [x] 5.3 Implement _build_tree recursive method


    - Accept DirectoryNode, rich Tree, and depth parameters
    - Respect max_depth constraint
    - Format directories using _format_directory
    - Format files using _format_file
    - Respect max_files_per_dir constraint
    - Add ellipsis for truncated content
    - _Requirements: 3.2, 8.2, 8.3, 8.4_
  
  - [x] 5.4 Implement _format_file method


    - Accept file path and category parameters
    - Apply color based on file category
    - Return formatted string with rich markup
    - _Requirements: 3.4_
  
  - [x] 5.5 Implement _format_directory method


    - Accept directory name and is_new flag
    - Apply bold styling for directories
    - Add indicator for new directories
    - Return formatted string with rich markup
    - _Requirements: 11.1_
  
  - [x] 5.6 Write property test for emoji exclusion


    - **Property 5: Tree rendering idempotence**
    - **Validates: Requirements 3.2, 3.3, 9.3**
  
  - [x] 5.7 Implement fallback SimpleTreeRenderer


    - Create SimpleTreeRenderer class for when rich is unavailable
    - Use ASCII characters (|, +, -) for tree structure
    - Implement same interface as TreeRenderer
    - _Requirements: 12.3_

- [x] 6. Implement TreeComparator





  - [x] 6.1 Implement display_comparison static method


    - Accept before and after DirectorySnapshot parameters
    - Call StatisticsCalculator.calculate_delta
    - Display comparison header
    - Display file count delta with _format_delta
    - Display directory count delta with _format_delta
    - Display size delta with _format_delta
    - Display depth delta with _format_delta
    - Display category deltas
    - Calculate and display percentage changes
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [x] 6.2 Implement _format_delta static method


    - Accept value, show_percentage, and base_value parameters
    - Add +/- prefix based on value sign
    - Apply green color for positive, red for negative
    - Calculate percentage if show_percentage is True
    - Return formatted string with rich markup
    - _Requirements: 6.5, 6.6_

- [x] 7. Implement TreeVisualizer orchestrator





  - [x] 7.1 Implement __init__


    - Accept root_path and TreeRenderer parameters
    - Initialize DirectoryScanner with FileClassifier
    - Store renderer reference
    - _Requirements: 10.2, 10.5_
  
  - [x] 7.2 Implement capture_before_state method


    - Call DirectoryScanner.scan with root_path
    - Return DirectorySnapshot
    - _Requirements: 1.3, 4.1_
  
  - [x] 7.3 Implement capture_after_state method


    - Call DirectoryScanner.scan with root_path
    - Return DirectorySnapshot
    - _Requirements: 1.4, 5.1_
  
  - [x] 7.4 Implement simulate_after_state method


    - Accept DryRunStats parameter
    - Create simulated DirectoryNode tree based on DryRunStats
    - Mark new directories with is_new flag
    - Calculate simulated statistics
    - Return DirectorySnapshot with is_simulated=True
    - _Requirements: 7.2, 7.3_
  
  - [x] 7.5 Write property test for dry-run simulation accuracy


    - **Property 4: Dry-run simulation accuracy**
    - **Validates: Requirements 7.2, 7.3**
  
  - [x] 7.6 Implement render_before_tree method


    - Accept DirectorySnapshot parameter
    - Display "BEFORE" header with separator
    - Call TreeRenderer.render with snapshot
    - Display statistics from snapshot
    - Display separator after tree
    - _Requirements: 4.1, 4.4, 4.5_
  
  - [x] 7.7 Implement render_after_tree method


    - Accept DirectorySnapshot and is_simulated parameters
    - Display "AFTER" header with simulation indicator if needed
    - Call TreeRenderer.render with snapshot
    - Display statistics from snapshot
    - Display separator after tree
    - _Requirements: 5.1, 5.4, 7.4_
  
  - [x] 7.8 Implement display_comparison method


    - Accept before and after DirectorySnapshot parameters
    - Call TreeComparator.display_comparison
    - _Requirements: 6.1_
  
  - [x] 7.9 Write property test for file conservation


    - **Property 10: Before-after file conservation**
    - **Validates: Requirements 1.3, 1.4, 5.3**

- [x] 8. Integrate tree visualization into CLI





  - [x] 8.1 Add --tree flag to folder command


    - Add tree parameter to folder function signature
    - Add typer.Option for --tree flag with help text
    - _Requirements: 1.1, 1.5_
  
  - [x] 8.2 Implement tree visualization workflow for actual execution


    - Check if tree flag is enabled
    - Create TreeVisualizer instance
    - Capture before state before calling organizer.organize()
    - Render before tree
    - Execute organizer.organize()
    - Capture after state after organize completes
    - Render after tree
    - Display comparison
    - _Requirements: 1.1, 1.3, 1.4, 9.1, 9.2_
  
  - [x] 8.3 Implement tree visualization workflow for dry-run mode


    - Check if both tree and dry flags are enabled
    - Create TreeVisualizer instance
    - Capture before state
    - Render before tree
    - Execute organizer.organize() to get DryRunStats
    - Simulate after state from DryRunStats
    - Render after tree with simulation indicator
    - Display comparison
    - _Requirements: 1.2, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 8.4 Ensure standard output is preserved


    - Verify DryRunFormatter output still displays after tree visualization
    - Verify actual mode statistics still display after tree visualization
    - _Requirements: 9.4_

- [x] 9. Add error handling and edge cases





  - [x] 9.1 Handle permission errors in DirectoryScanner


    - Catch PermissionError during traversal
    - Add marker to DirectoryNode for restricted access
    - Continue scanning accessible portions
    - _Requirements: 12.4_
  
  - [x] 9.2 Handle rendering failures in TreeRenderer


    - Wrap render calls in try-except
    - Log errors and continue with cleanup operation
    - Display error message to user
    - _Requirements: 12.1_
  
  - [x] 9.3 Handle statistics calculation failures


    - Catch exceptions in StatisticsCalculator
    - Return partial statistics with error indicators
    - Display warning about incomplete statistics
    - _Requirements: 12.2_
  
  - [x] 9.4 Implement rich library availability check


    - Check if rich can be imported at module level
    - Set RICH_AVAILABLE flag
    - Use SimpleTreeRenderer if rich unavailable
    - _Requirements: 12.3_

- [x] 10. Write integration tests





  - [x] 10.1 Test --tree flag with actual execution


    - Create temporary directory with sample files
    - Execute scrubb folder --tree
    - Verify before tree is displayed
    - Verify after tree is displayed
    - Verify comparison is displayed
    - Verify files are actually moved
    - _Requirements: 1.1_
  
  - [x] 10.2 Test --tree --dry flags together

    - Create temporary directory with sample files
    - Execute scrubb folder --tree --dry
    - Verify before tree is displayed
    - Verify simulated after tree is displayed
    - Verify simulation indicator is present
    - Verify no files are moved
    - _Requirements: 1.2, 7.5_
  
  - [x] 10.3 Test tree visualization with various directory sizes

    - Test with empty directory
    - Test with single file
    - Test with nested directories
    - Test with large directory (100+ files)
    - _Requirements: 4.2, 4.3, 5.2_
  
  - [x] 10.4 Test output ordering

    - Verify trees display before standard output
    - Verify statistics display after trees
    - Verify comparison displays between trees and standard output
    - _Requirements: 9.1, 9.2_

- [x] 11. Update documentation




  - [x] 11.1 Update COMMAND_REFERENCE.md


    - Add --tree flag documentation to folder command
    - Add examples of --tree usage
    - Add examples of --tree --dry usage
    - Document tree output format
    - Document statistics displayed
    - _Requirements: 1.1, 1.2_
  
  - [x] 11.2 Update README.md


    - Add tree visualization feature to feature list
    - Add example output screenshots or text
    - Add usage examples
    - _Requirements: 1.1_

- [x] 12. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
