"""Property-based tests for StatisticsCalculator."""

import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings

from scrubb.tree_models import DirectoryNode, DirectoryStatistics, StatisticsDelta
from scrubb.file_classifier import FileClassifier, FileCategory
from scrubb.statistics_calculator import StatisticsCalculator


# Strategy for generating file categories
@st.composite
def file_category_strategy(draw):
    """Generate a FileCategory for testing."""
    categories = [
        FileCategory.IMAGE,
        FileCategory.VIDEO,
        FileCategory.MARKDOWN,
        FileCategory.DOCUMENT,
        FileCategory.DEVELOPMENT,
        FileCategory.UNKNOWN
    ]
    return draw(st.sampled_from(categories))


# Strategy for generating DirectoryNode trees
@st.composite
def directory_tree_strategy(draw, current_depth=0, max_depth=2):
    """Generate a random DirectoryNode tree structure."""
    is_directory = draw(st.booleans()) if current_depth < max_depth else False
    
    # Generate a simple name
    name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz",
        min_size=1,
        max_size=8
    ))
    
    path = Path(f"/test/{name}")
    
    if is_directory and current_depth < max_depth:
        # Directory node - limit children
        num_children = draw(st.integers(min_value=0, max_value=3))
        children = []
        
        for _ in range(num_children):
            child = draw(directory_tree_strategy(current_depth=current_depth + 1, max_depth=max_depth))
            child.depth = current_depth + 1
            children.append(child)
        
        return DirectoryNode(
            path=path,
            name=name,
            is_directory=True,
            size=0,
            children=children,
            category=None,
            depth=current_depth,
            is_new=False,
            is_removed=False
        )
    else:
        # File node
        size = draw(st.integers(min_value=0, max_value=10000))
        category = draw(file_category_strategy())
        
        return DirectoryNode(
            path=path,
            name=name,
            is_directory=False,
            size=size,
            children=[],
            category=category,
            depth=current_depth,
            is_new=False,
            is_removed=False
        )


class TestStatisticsCalculation:
    """Property tests for statistics calculation correctness."""
    
    @settings(max_examples=100)
    @given(tree=directory_tree_strategy())
    def test_statistics_calculation_correctness(self, tree):
        """
        **Feature: tree-visualization, Property 2: Statistics calculation correctness**
        **Validates: Requirements 2.1, 2.5**
        
        For any directory tree, the sum of files in all categories should equal
        the total file count in the statistics.
        """
        classifier = FileClassifier()
        stats = StatisticsCalculator.calculate(tree, classifier)
        
        # Calculate expected total from categories
        total_from_categories = sum(stats.files_by_category.values())
        
        # Verify that sum of category counts equals total file count
        assert stats.total_files == total_from_categories, \
            f"Category sum mismatch: total_files={stats.total_files}, " \
            f"sum of categories={total_from_categories}"
        
        # Verify all counts are non-negative
        assert stats.total_files >= 0, "total_files should be non-negative"
        assert stats.total_directories >= 0, "total_directories should be non-negative"
        assert stats.total_size >= 0, "total_size should be non-negative"
        assert stats.max_depth >= 0, "max_depth should be non-negative"
        
        # Verify category counts are non-negative
        for category, count in stats.files_by_category.items():
            assert count >= 0, f"Category {category} count should be non-negative"
        
        # Verify size by category sums to total size
        total_size_from_categories = sum(stats.size_by_category.values())
        assert stats.total_size == total_size_from_categories, \
            f"Size sum mismatch: total_size={stats.total_size}, " \
            f"sum of category sizes={total_size_from_categories}"


class TestDeltaCalculation:
    """Property tests for delta calculation symmetry."""
    
    @settings(max_examples=100)
    @given(
        tree1=directory_tree_strategy(),
        tree2=directory_tree_strategy()
    )
    def test_delta_calculation_symmetry(self, tree1, tree2):
        """
        **Feature: tree-visualization, Property 3: Delta calculation symmetry**
        **Validates: Requirements 6.2, 6.3, 6.4, 6.5**
        
        For any two directory snapshots A and B, the delta from A to B should be
        the negation of the delta from B to A.
        """
        classifier = FileClassifier()
        
        # Calculate statistics for both trees
        stats1 = StatisticsCalculator.calculate(tree1, classifier)
        stats2 = StatisticsCalculator.calculate(tree2, classifier)
        
        # Calculate deltas in both directions
        delta_1_to_2 = StatisticsCalculator.calculate_delta(stats1, stats2)
        delta_2_to_1 = StatisticsCalculator.calculate_delta(stats2, stats1)
        
        # Verify symmetry for basic metrics
        assert delta_1_to_2.files_delta == -delta_2_to_1.files_delta, \
            f"Files delta not symmetric: {delta_1_to_2.files_delta} vs {-delta_2_to_1.files_delta}"
        
        assert delta_1_to_2.directories_delta == -delta_2_to_1.directories_delta, \
            f"Directories delta not symmetric: {delta_1_to_2.directories_delta} vs {-delta_2_to_1.directories_delta}"
        
        assert delta_1_to_2.size_delta == -delta_2_to_1.size_delta, \
            f"Size delta not symmetric: {delta_1_to_2.size_delta} vs {-delta_2_to_1.size_delta}"
        
        assert delta_1_to_2.depth_delta == -delta_2_to_1.depth_delta, \
            f"Depth delta not symmetric: {delta_1_to_2.depth_delta} vs {-delta_2_to_1.depth_delta}"
        
        # Verify symmetry for category deltas
        all_categories = set(delta_1_to_2.category_deltas.keys()) | set(delta_2_to_1.category_deltas.keys())
        
        for category in all_categories:
            delta_1_to_2_cat = delta_1_to_2.category_deltas.get(category, 0)
            delta_2_to_1_cat = delta_2_to_1.category_deltas.get(category, 0)
            
            assert delta_1_to_2_cat == -delta_2_to_1_cat, \
                f"Category {category} delta not symmetric: {delta_1_to_2_cat} vs {-delta_2_to_1_cat}"
