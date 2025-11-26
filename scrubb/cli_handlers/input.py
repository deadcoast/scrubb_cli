"""CLI input handling with validation.

This module provides input handling for CLI commands with proper
validation and security checks.
"""

from __future__ import annotations
from pathlib import Path

from rich.prompt import Prompt, Confirm

from ..io.path_validator import PathValidator
from ..core.result import Result
from ..core.errors import ValidationError


class InputHandler:
    """Handles CLI input with validation.
    
    This class provides methods for prompting users for input
    with proper validation and security checks.
    """
    
    def __init__(self, path_validator: PathValidator):
        """Initialize the input handler.
        
        Args:
            path_validator: PathValidator instance for security checks
        """
        self.path_validator = path_validator
    
    def prompt_for_path(
        self,
        message: str,
        root: Path,
        default: str | None = None,
        must_exist: bool = True
    ) -> Path:
        """Prompt for path with validation.
        
        Args:
            message: The prompt message to display
            root: Root path for validation
            default: Optional default path value
            must_exist: Whether the path must exist
            
        Returns:
            Path: Validated path
            
        Raises:
            KeyboardInterrupt: If user cancels with Ctrl+C
            ValidationError: If path validation fails after max retries
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get user input
                path_input = Prompt.ask(message, default=default)
                
                # Validate the input
                result = self.validate_path_input(path_input, root, must_exist)
                
                if result.is_success():
                    return result.unwrap()
                else:
                    # Show error and retry
                    error = result.error
                    Prompt.ask(
                        f"[red]Error:[/red] {error}\nPress Enter to try again",
                        default=""
                    )
                    retry_count += 1
                    
            except KeyboardInterrupt:
                # Re-raise to allow graceful handling by caller
                raise
        
        # Max retries reached
        raise ValidationError(
            "Maximum path validation retries reached",
            context={"max_retries": max_retries}
        )
    
    def prompt_for_confirmation(
        self,
        message: str,
        default: bool = False
    ) -> bool:
        """Prompt for yes/no confirmation.
        
        Args:
            message: The confirmation message to display
            default: Default value if user presses Enter
            
        Returns:
            bool: True if user confirms, False otherwise
            
        Raises:
            KeyboardInterrupt: If user cancels with Ctrl+C
        """
        try:
            return Confirm.ask(message, default=default)
        except KeyboardInterrupt:
            # Re-raise to allow graceful handling by caller
            raise
    
    def validate_path_input(
        self,
        path_input: str,
        root: Path,
        must_exist: bool = True
    ) -> Result[Path]:
        """Validate path input.
        
        This method:
        1. Strips quotes from input
        2. Expands user home directory (~)
        3. Validates path security
        4. Optionally checks if path exists
        
        Args:
            path_input: User-provided path string
            root: Root path for validation
            must_exist: Whether the path must exist
            
        Returns:
            Result[Path]: Validated path on success, error on failure
        """
        # Strip quotes from path input (handles both single and double quotes)
        path_input = path_input.strip().strip('"').strip("'")
        
        # Expand user home directory
        path_obj = Path(path_input).expanduser()
        
        # Resolve to absolute path
        if not path_obj.is_absolute():
            path_obj = root / path_obj
        
        path_obj = path_obj.resolve()
        
        # Validate path security
        validation_result = self.path_validator.validate(path_obj, root)
        
        if validation_result.is_failure():
            return validation_result
        
        validated_path = validation_result.unwrap()
        
        # Check if path exists (if required)
        if must_exist:
            if not validated_path.exists():
                from ..core.result import Failure
                return Failure(ValidationError(
                    f"Path does not exist: {validated_path}",
                    context={"path": str(validated_path)}
                ))
        
        return validation_result
