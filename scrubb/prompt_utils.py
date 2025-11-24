"""Prompt utilities for interactive CLI operations."""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from rich.prompt import Prompt, Confirm


class PromptUtils:
    """Utilities for interactive prompts with validation."""
    
    @staticmethod
    def prompt_directory(message: str, default: Optional[str] = None) -> Path:
        """
        Prompt for directory path with validation.
        
        Args:
            message: The prompt message to display
            default: Optional default path value
            
        Returns:
            Path: Validated directory path
            
        Raises:
            KeyboardInterrupt: If user cancels with Ctrl+C
        """
        while True:
            try:
                # Get user input
                path_input = Prompt.ask(message, default=default)
                
                # Strip quotes from path input (handles both single and double quotes)
                path_input = path_input.strip().strip('"').strip("'")
                
                # Resolve path (handle absolute, relative, and tilde expansion)
                target_path = Path(path_input).expanduser().resolve()
                
                # Validate that path exists and is a directory
                if not target_path.exists():
                    Prompt.ask(
                        f"[red]Error:[/red] Path does not exist: {target_path}\nPress Enter to try again",
                        default=""
                    )
                    continue
                
                if not target_path.is_dir():
                    Prompt.ask(
                        f"[red]Error:[/red] Path is not a directory: {target_path}\nPress Enter to try again",
                        default=""
                    )
                    continue
                
                return target_path
                
            except KeyboardInterrupt:
                # Re-raise to allow graceful handling by caller
                raise
    
    @staticmethod
    def prompt_confirmation(message: str, default: bool = False) -> bool:
        """
        Prompt for yes/no confirmation.
        
        Accepts common affirmative responses: 'yes', 'y', 'Y', 'YES', or Enter (if default is True)
        Accepts common negative responses: 'no', 'n', 'N', 'NO'
        
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
    
    @staticmethod
    def prompt_choice(message: str, choices: list[str]) -> str:
        """
        Prompt for selection from numbered choices.
        
        Args:
            message: The prompt message to display
            choices: List of choice options
            
        Returns:
            str: The selected choice
            
        Raises:
            KeyboardInterrupt: If user cancels with Ctrl+C
            ValueError: If choices list is empty
        """
        if not choices:
            raise ValueError("Choices list cannot be empty")
        
        try:
            # Display numbered options
            choice_str = "\n".join(f"{i+1}. {choice}" for i, choice in enumerate(choices))
            full_message = f"{message}\n{choice_str}\n\nEnter choice number"
            
            while True:
                # Get user input
                response = Prompt.ask(full_message)
                
                try:
                    # Try to parse as number
                    choice_num = int(response)
                    if 1 <= choice_num <= len(choices):
                        return choices[choice_num - 1]
                    else:
                        Prompt.ask(
                            f"[red]Error:[/red] Please enter a number between 1 and {len(choices)}\nPress Enter to try again",
                            default=""
                        )
                except ValueError:
                    # Not a valid number
                    Prompt.ask(
                        "[red]Error:[/red] Please enter a valid number\nPress Enter to try again",
                        default=""
                    )
                    
        except KeyboardInterrupt:
            # Re-raise to allow graceful handling by caller
            raise
