import os
import platform
import sys
from pathlib import Path
from apps.config.ui import UI

class ConfigManager:
    """Class for managing shell configuration and aliases."""

    # Alias markers
    MARKER_START = "# Dagger tool alias - do not edit\n"
    MARKER_END = "# End dagger tool alias\n"

    @staticmethod
    def get_shell_config_file() -> str:
        """
        Determine the shell configuration file based on the platform.

        Returns:
            Path to the shell configuration file.
        """
        home_dir = os.path.expanduser("~")
        if platform.system() == "Windows":
            return os.path.join(home_dir, "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1")

        shell = os.environ.get('SHELL', '').split('/')[-1]
        if shell == "zsh":
            return os.path.join(home_dir, ".zshrc")
        elif platform.system() == "Darwin":
            return os.path.join(home_dir, ".bash_profile")
        return os.path.join(home_dir, ".bashrc")

    @classmethod
    def is_alias_set(cls, config_file: str) -> bool:
        """
        Check if the 'dagger' alias is present in the config file.

        Args:
            config_file: Path to the shell configuration file.

        Returns:
            True if alias is set, False otherwise.
        """
        if not os.path.exists(config_file):
            return False
        try:
            with open(config_file, "r") as f:
                return cls.MARKER_START in f.read()
        except IOError as e:
            UI.show_error(f"Reading config file: {e}")
            return False

    @classmethod
    def add_alias(cls) -> None:
        """Add the 'dagger' alias to the shell configuration file."""
        config_file = cls.get_shell_config_file()
        # Determine path to the main script using pathlib
        script_path = Path(__file__).resolve().parents[2] / "main.py"
        # Use the current Python executable for the alias
        if platform.system() == "Windows":
            # PowerShell function alias
            alias_line = f"function dagger {{ & '{sys.executable}' '{script_path}' }}\n"
        else:
            alias_line = f"alias dagger='{sys.executable} {script_path}'\n"

        if cls.is_alias_set(config_file):
            UI.show_message("Alias 'dagger' is already set.", color=UI.Color.YELLOW)
            return

        try:
            if platform.system() == "Windows" and not os.path.exists(os.path.dirname(config_file)):
                os.makedirs(os.path.dirname(config_file))

            with open(config_file, "a") as f:
                f.write(f"\n{cls.MARKER_START}{alias_line}{cls.MARKER_END}")

            msg = (f"Alias 'dagger' added to {config_file}. Restart your shell or run 'source {config_file}'."
                   if platform.system() != "Windows" else
                   f"Alias 'dagger' added to {config_file}. Restart PowerShell.")
            UI.show_message(msg, color=UI.Color.GREEN)
        except IOError as e:
            UI.show_error(f"Adding alias: {e}")

    @classmethod
    def remove_alias(cls) -> None:
        """Remove the 'dagger' alias from the shell configuration file."""
        config_file = cls.get_shell_config_file()

        if not os.path.exists(config_file):
            UI.show_message(f"Configuration file {config_file} does not exist.", color=UI.Color.YELLOW)
            return

        try:
            with open(config_file, "r") as f:
                lines = f.readlines()

            new_lines = []
            skip = False
            for line in lines:
                if line.strip() == cls.MARKER_START.strip():
                    skip = True
                elif line.strip() == cls.MARKER_END.strip():
                    skip = False
                    continue

                if not skip:
                    new_lines.append(line)

            with open(config_file, "w") as f:
                f.writelines(new_lines)

            msg = (f"Alias 'dagger' removed from {config_file}. Restart your shell or run 'source {config_file}'."
                   if platform.system() != "Windows" else
                   f"Alias 'dagger' removed from {config_file}. Restart PowerShell.")
            UI.show_message(msg, color=UI.Color.GREEN)
        except IOError as e:
            UI.show_error(f"Removing alias: {e}")