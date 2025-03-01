# ui.py
from typing import List
import os

class UI:
    """Enhanced class for professional UI rendering and interactions."""

    # Enhanced box drawing characters with style options
    class Style:
        HORIZONTAL = '─'
        VERTICAL = '│'
        TOP_LEFT = '┌'
        TOP_RIGHT = '┐'
        BOTTOM_LEFT = '└'
        BOTTOM_RIGHT = '┘'
        LEFT_T = '├'
        RIGHT_T = '┤'
        SEPARATOR_MARKER = "__SEPARATOR__"
        PADDING = 2  # Padding inside boxes

    # ANSI color codes for professional styling
    class Color:
        RESET = '\033[0m'
        BOLD = '\033[1m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        CYAN = '\033[96m'
        GRAY = '\033[90m'

    @classmethod
    def clear_screen(cls) -> None:
        """Clear the terminal screen for a fresh display."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @classmethod
    def draw_box(cls, content: List[str], center_title: bool = False, title_color: str = Color.BLUE,
                 text_color: str = Color.RESET, border_color: str = Color.CYAN) -> None:
        """
        Draw an enhanced box with color and better formatting.

        Args:
            content: List of strings to display, with "__SEPARATOR__" for separators.
            center_title: If True, center the first line (title).
            title_color: ANSI color code for the title.
            text_color: ANSI color code for the text.
            border_color: ANSI color code for the borders.
        """
        cls.clear_screen()  # Fresh screen for each redraw
        text_lines = [line for line in content if line != cls.Style.SEPARATOR_MARKER]
        if not text_lines:
            return

        max_length = max(len(line) for line in text_lines)
        internal_width = max_length + (2 * cls.Style.PADDING)
        top_border = f"{border_color}{cls.Style.TOP_LEFT}{cls.Style.HORIZONTAL * internal_width}{cls.Style.TOP_RIGHT}{cls.Color.RESET}"
        bottom_border = f"{border_color}{cls.Style.BOTTOM_LEFT}{cls.Style.HORIZONTAL * internal_width}{cls.Style.BOTTOM_RIGHT}{cls.Color.RESET}"
        separator = f"{border_color}{cls.Style.LEFT_T}{cls.Style.HORIZONTAL * internal_width}{cls.Style.RIGHT_T}{cls.Color.RESET}"

        print(top_border)
        for i, line in enumerate(content):
            if line == cls.Style.SEPARATOR_MARKER:
                print(separator)
            else:
                padding = ' ' * cls.Style.PADDING
                if center_title and i == 0:
                    formatted = f"{padding}{line}{padding}".center(internal_width)
                    print(
                        f"{border_color}{cls.Style.VERTICAL}{cls.Color.RESET}{title_color}{cls.Color.BOLD}{formatted}{cls.Color.RESET}{border_color}{cls.Style.VERTICAL}{cls.Color.RESET}")
                else:
                    formatted = f"{padding}{line}{padding}".ljust(internal_width)
                    print(
                        f"{border_color}{cls.Style.VERTICAL}{cls.Color.RESET}{text_color}{formatted}{cls.Color.RESET}{border_color}{cls.Style.VERTICAL}{cls.Color.RESET}")
        print(bottom_border)

    @classmethod
    def get_input(cls, prompt: str = " > ", prompt_color: str = Color.GREEN) -> str:
        """Get user input with styled prompt and error handling."""
        try:
            return input(f"{prompt_color}{cls.Color.BOLD}{prompt}{cls.Color.RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return "q"

    @classmethod
    def show_message(cls, message: str, color: str = Color.GREEN) -> None:
        """Display a styled message in a box."""
        cls.draw_box([message], text_color=color)

    @classmethod
    def show_error(cls, error_message: str) -> None:
        """Display a styled error message in a box."""
        cls.draw_box([f"Error: {error_message}"], text_color=cls.Color.RED, border_color=cls.Color.RED)