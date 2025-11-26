"""Property-based tests for core types (Result, errors, validation).

This module tests the core type system including Result types, error handling,
and validation functions to ensure they properly propagate errors and preserve context.
"""

import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
import tempfile
import re

from scrubb.core.result import Success, Failure, Result, OperationResult
from scrubb.core.errors import (
    ScrubbError,
    ValidationError,
    ConfigurationError,
    FileOperationError,
    DirectoryOperationError,
    PathSecurityError,
    ClassificationError,
)
from scrubb.core.validation import (
    validate_path_string,
    validate_path_exists,
    validate_directory_path,
    validate_file_path,
    validate_regex_pattern,
    validate_positive_integer,
    validate_non_negative_integer,
    validate_string_not_empty,
    validate_configuration_dict,
)


# Strategies for generating test data

@st.composite
def valid_path_strings(draw):
    """Generate valid path strings."""
    # Generate path components
    num_parts = draw(st.integers(min_value=1, max_value=5))
    parts = []
    for _ in range(num_parts):
        part = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
            min_size=1,
            max_size=10
        ))
        parts.append(part)
    
    return "/".join(parts)


@st.composite
def invalid_path_strings(draw):
    """Generate invalid path strings (empty or with null bytes)."""
    choice = draw(st.integers(min_value=0, max_value=1))
    if choice == 0:
        # Empty string
        return ""
    else:
        # String with null byte
        base = draw(st.text(min_size=1, max_size=10))
        return base + "\0" + draw(st.text(min_size=0, max_size=5))


@st.composite
def error_contexts(draw):
    """Generate error context dictionaries."""
    num_keys = draw(st.integers(min_value=0, max_value=5))
    context = {}
    for _ in range(num_keys):
        key = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz_",
            min_size=1,
            max_size=10
        ))
        value = draw(st.one_of(
            st.text(max_size=20),
            st.integers(),
            st.booleans(),
        ))
        context[key] = value
    return context


@st.composite
def error_messages(draw):
    """Generate error messages."""
    return draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-_",
        min_size=5,
        max_size=100
    ))


class TestErrorPropagation:
    """Property tests for error propagation.
    
    **Feature: architectural-unification, Property 4: Error Propagation**
    **Validates: Requirements 4.1**
    """
    
    @settings(max_examples=100)
    @given(invalid_path=invalid_path_strings())
    def test_invalid_path_string_raises_immediately(self, invalid_path):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any invalid path string (empty or with null bytes), validation should
        raise ValidationError immediately, not return partial results.
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_path_string(invalid_path)
        
        # Verify exception was raised
        assert exc_info.value is not None
        # Verify it's the correct exception type
        assert isinstance(exc_info.value, ValidationError)
        # Verify it has a message
        assert exc_info.value.message
    
    @settings(max_examples=100)
    @given(value=st.one_of(
        st.floats(),
        st.text(),
        st.booleans(),
        st.none(),
    ))
    def test_invalid_integer_type_raises_immediately(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any non-integer value, integer validation should raise ValidationError
        immediately, not attempt to convert or return partial results.
        """
        # Skip if value happens to be an integer (shouldn't happen with this strategy)
        assume(not isinstance(value, int))
        
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(value)
        
        # Verify exception was raised with correct type
        assert isinstance(exc_info.value, ValidationError)
        assert "must be an integer" in exc_info.value.message
    
    @settings(max_examples=100)
    @given(value=st.integers(max_value=0))
    def test_non_positive_integer_raises_immediately(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any non-positive integer, positive integer validation should raise
        ValidationError immediately.
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(value)
        
        # Verify exception was raised with correct type
        assert isinstance(exc_info.value, ValidationError)
        assert "must be positive" in exc_info.value.message
    
    @settings(max_examples=100)
    @given(value=st.integers(max_value=-1))
    def test_negative_integer_raises_immediately(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any negative integer, non-negative integer validation should raise
        ValidationError immediately.
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_non_negative_integer(value)
        
        # Verify exception was raised with correct type
        assert isinstance(exc_info.value, ValidationError)
        assert "must be non-negative" in exc_info.value.message
    
    @settings(max_examples=100)
    @given(value=st.one_of(
        st.integers(),
        st.floats(),
        st.booleans(),
        st.none(),
    ))
    def test_non_string_raises_immediately(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any non-string value, string validation should raise ValidationError
        immediately.
        """
        # Skip if value happens to be a string
        assume(not isinstance(value, str))
        
        with pytest.raises(ValidationError) as exc_info:
            validate_string_not_empty(value)
        
        # Verify exception was raised with correct type
        assert isinstance(exc_info.value, ValidationError)
        assert "must be a string" in exc_info.value.message
    
    @settings(max_examples=100)
    @given(value=st.text(max_size=10).filter(lambda x: not x.strip()))
    def test_empty_string_raises_immediately(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any empty or whitespace-only string, string validation should raise
        ValidationError immediately.
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_string_not_empty(value)
        
        # Verify exception was raised with correct type
        assert isinstance(exc_info.value, ValidationError)
        assert "cannot be empty" in exc_info.value.message
    
    @settings(max_examples=100)
    @given(pattern=st.text(min_size=1, max_size=20).filter(
        lambda x: not _is_valid_regex(x)
    ))
    def test_invalid_regex_raises_immediately(self, pattern):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any invalid regex pattern, regex validation should raise ValidationError
        immediately.
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_regex_pattern(pattern)
        
        # Verify exception was raised with correct type
        assert isinstance(exc_info.value, ValidationError)
        assert "Invalid regex pattern" in exc_info.value.message


class TestResultTypes:
    """Property tests for Result types.
    
    **Feature: architectural-unification, Property 4: Error Propagation**
    **Validates: Requirements 4.1**
    """
    
    @settings(max_examples=100)
    @given(value=st.one_of(
        st.integers(),
        st.text(),
        st.booleans(),
        st.lists(st.integers()),
    ))
    def test_success_wraps_value_correctly(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any value, Success should properly wrap it and allow unwrapping.
        """
        result = Success(value)
        
        # Verify Success properties
        assert result.is_success()
        assert not result.is_failure()
        
        # Verify unwrap returns the value
        assert result.unwrap() == value
        
        # Verify unwrap_or returns the value (not default)
        default = "default_value"
        assert result.unwrap_or(default) == value
    
    @settings(max_examples=100)
    @given(
        error_msg=error_messages(),
        context=error_contexts()
    )
    def test_failure_wraps_error_correctly(self, error_msg, context):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any error, Failure should properly wrap it and raise on unwrap.
        """
        error = ValidationError(error_msg, context=context)
        result = Failure(error)
        
        # Verify Failure properties
        assert not result.is_success()
        assert result.is_failure()
        
        # Verify unwrap raises the error
        with pytest.raises(ValidationError) as exc_info:
            result.unwrap()
        
        assert exc_info.value == error
    
    @settings(max_examples=100)
    @given(
        error_msg=error_messages(),
        context=error_contexts(),
        default_value=st.integers()
    )
    def test_failure_unwrap_or_returns_default(self, error_msg, context, default_value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any Failure, unwrap_or should return the default value.
        """
        error = ValidationError(error_msg, context=context)
        result = Failure(error)
        
        # Verify unwrap_or returns default
        assert result.unwrap_or(default_value) == default_value
    
    @settings(max_examples=100)
    @given(
        files_moved=st.integers(min_value=0, max_value=1000),
        empty_folders_removed=st.integers(min_value=0, max_value=100),
        num_critical=st.integers(min_value=0, max_value=10),
        num_warnings=st.integers(min_value=0, max_value=10),
    )
    def test_operation_result_success_property(
        self, files_moved, empty_folders_removed, num_critical, num_warnings
    ):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any OperationResult, success property should be True only when there
        are no critical errors.
        """
        # Create errors
        critical_errors = [
            FileOperationError(f"Critical error {i}")
            for i in range(num_critical)
        ]
        warnings = [
            DirectoryOperationError(f"Warning {i}")
            for i in range(num_warnings)
        ]
        
        result = OperationResult(
            files_moved=files_moved,
            files_by_category={},
            empty_folders_removed=empty_folders_removed,
            critical_errors=critical_errors,
            warnings=warnings,
        )
        
        # Verify success property
        if num_critical == 0:
            assert result.success
        else:
            assert not result.success
        
        # Verify total_errors property
        assert result.total_errors == num_critical + num_warnings


class TestErrorContext:
    """Property tests for error context preservation.
    
    **Feature: architectural-unification, Property 4: Error Propagation**
    **Validates: Requirements 4.1**
    """
    
    @settings(max_examples=100)
    @given(
        error_msg=error_messages(),
        context=error_contexts()
    )
    def test_scrubb_error_preserves_context(self, error_msg, context):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any error with context, ScrubbError should preserve the context dictionary.
        """
        error = ScrubbError(error_msg, context=context)
        
        # Verify message is preserved
        assert error.message == error_msg
        
        # Verify context is preserved
        assert error.context == context
        
        # Verify string representation includes context
        error_str = str(error)
        assert error_msg in error_str
        
        # If context is not empty, verify it appears in string
        if context:
            for key in context:
                assert key in error_str
    
    @settings(max_examples=100)
    @given(
        error_msg=error_messages(),
        context=error_contexts()
    )
    def test_validation_error_preserves_context(self, error_msg, context):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any ValidationError with context, the context should be preserved.
        """
        error = ValidationError(error_msg, context=context)
        
        # Verify it's a ScrubbError subclass
        assert isinstance(error, ScrubbError)
        
        # Verify message and context are preserved
        assert error.message == error_msg
        assert error.context == context
    
    @settings(max_examples=100)
    @given(
        error_msg=error_messages(),
        context=error_contexts()
    )
    def test_all_error_types_preserve_context(self, error_msg, context):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any error type with context, the context should be preserved.
        """
        error_types = [
            ValidationError,
            ConfigurationError,
            FileOperationError,
            DirectoryOperationError,
            PathSecurityError,
            ClassificationError,
        ]
        
        for error_type in error_types:
            error = error_type(error_msg, context=context)
            
            # Verify it's a ScrubbError subclass
            assert isinstance(error, ScrubbError)
            
            # Verify message and context are preserved
            assert error.message == error_msg
            assert error.context == context
            
            # Verify string representation includes message
            error_str = str(error)
            assert error_msg in error_str
    
    @settings(max_examples=100)
    @given(invalid_path=invalid_path_strings())
    def test_validation_error_includes_context_in_exception(self, invalid_path):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any validation failure, the raised exception should include context
        about what failed.
        """
        with pytest.raises(ValidationError) as exc_info:
            validate_path_string(invalid_path)
        
        error = exc_info.value
        
        # Verify context exists
        assert error.context is not None
        assert isinstance(error.context, dict)
        
        # Verify context includes the path
        assert "path" in error.context
        assert error.context["path"] == invalid_path
    
    @settings(max_examples=100)
    @given(value=st.one_of(st.floats(), st.text(), st.booleans()))
    def test_type_validation_error_includes_type_in_context(self, value):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any type validation failure, the raised exception should include
        the actual type in the context.
        """
        # Skip if value happens to be an integer
        assume(not isinstance(value, int))
        
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(value)
        
        error = exc_info.value
        
        # Verify context includes type information
        assert "type" in error.context
        assert error.context["type"] == type(value).__name__


class TestResultTypeIntegration:
    """Integration tests for Result types with validation.
    
    **Feature: architectural-unification, Property 4: Error Propagation**
    **Validates: Requirements 4.1**
    """
    
    @settings(max_examples=100)
    @given(valid_path=valid_path_strings())
    def test_success_result_from_valid_input(self, valid_path):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any valid input, validation should succeed and can be wrapped in Success.
        """
        # Validate the path string
        validated = validate_path_string(valid_path)
        
        # Wrap in Success
        result = Success(validated)
        
        # Verify we can unwrap successfully
        assert result.unwrap() == valid_path
        assert result.is_success()
    
    @settings(max_examples=100)
    @given(invalid_path=invalid_path_strings())
    def test_failure_result_from_invalid_input(self, invalid_path):
        """
        **Feature: architectural-unification, Property 4: Error Propagation**
        **Validates: Requirements 4.1**
        
        For any invalid input, validation should raise an error that can be
        wrapped in Failure.
        """
        try:
            validate_path_string(invalid_path)
            # Should not reach here
            assert False, "Expected ValidationError to be raised"
        except ValidationError as e:
            # Wrap in Failure
            result = Failure(e)
            
            # Verify Failure properties
            assert result.is_failure()
            assert not result.is_success()
            
            # Verify unwrap raises the original error
            with pytest.raises(ValidationError):
                result.unwrap()


# Helper functions

def _is_valid_regex(pattern: str) -> bool:
    """Check if a string is a valid regex pattern."""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False
