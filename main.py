import os
import sys
import platform
from typing import List

from apps.config.app_manager import AppManager
from apps.config.ui import UI


class ConfigManager:
    """Class for managing shell configuration and aliases."""

    # Alias markers
    MARKER_START = "# Config tool alias - do not edit\n"
    MARKER_END = "# End config tool alias\n"

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
        Check if the 'config' alias is present in the config file.

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
        """Add the 'config' alias to the shell configuration file."""
        config_file = cls.get_shell_config_file()
        script_path = os.path.abspath(__file__)

        alias_line = (f"function config {{ python3 '{script_path}' }}\n" if platform.system() == "Windows"
                      else f"alias config='python3 {script_path}'\n")

        if cls.is_alias_set(config_file):
            UI.show_message("Alias 'config' is already set.", color=UI.Color.YELLOW)
            return

        try:
            if platform.system() == "Windows" and not os.path.exists(os.path.dirname(config_file)):
                os.makedirs(os.path.dirname(config_file))

            with open(config_file, "a") as f:
                f.write(f"\n{cls.MARKER_START}{alias_line}{cls.MARKER_END}")

            msg = (f"Alias 'config' added to {config_file}. Restart your shell or run 'source {config_file}'."
                   if platform.system() != "Windows" else
                   f"Alias 'config' added to {config_file}. Restart PowerShell.")
            UI.show_message(msg, color=UI.Color.GREEN)
        except IOError as e:
            UI.show_error(f"Adding alias: {e}")

    @classmethod
    def remove_alias(cls) -> None:
        """Remove the 'config' alias from the shell configuration file."""
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

            msg = (f"Alias 'config' removed from {config_file}. Restart your shell or run 'source {config_file}'."
                   if platform.system() != "Windows" else
                   f"Alias 'config' removed from {config_file}. Restart PowerShell.")
            UI.show_message(msg, color=UI.Color.GREEN)
        except IOError as e:
            UI.show_error(f"Removing alias: {e}")


class ConfigTool:
    """Main class for the configuration tool."""

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        apps_dir = os.path.join(script_dir, "apps")
        self.app_manager = AppManager(apps_dir)

    def build_menu_content(self, apps: List[str], alias_set: bool) -> List[str]:
        """
        Build the content list for the main menu.

        Args:
            apps: List of available app names.
            alias_set: Whether the 'config' alias is set.

        Returns:
            Lines for the menu, including title and separators.
        """
        content = ["Config Tool", UI.Style.SEPARATOR_MARKER]
        if apps:
            content.append("Available Apps:")
            for i, app in enumerate(apps, 1):
                content.append(f"{i}. {app}")
        else:
            content.append("No apps available yet.")
        content.append(UI.Style.SEPARATOR_MARKER)
        content.append("Options:")
        content.append("n. Create new sample app")
        content.append("r. Remove alias 'config'" if alias_set else "a. Add alias 'config'")
        content.append("q. Quit")
        return content

    def main_menu(self) -> None:
        """Display the interactive main menu."""
        try:
            while True:
                config_file = ConfigManager.get_shell_config_file()
                alias_set = ConfigManager.is_alias_set(config_file)
                apps = self.app_manager.list_apps()
                content = self.build_menu_content(apps, alias_set)
                UI.draw_box(content, center_title=True, title_color=UI.Color.BLUE)

                choice = UI.get_input(prompt="> ")

                if choice == "q":
                    UI.show_message("Exiting Config Tool.", color=UI.Color.YELLOW)
                    break
                elif choice == "n":
                    try:
                        app_name = input(f"{UI.Color.CYAN}Enter the name for the new app: {UI.Color.RESET}").strip()
                        if app_name:
                            self.app_manager.create_sample_app(app_name)
                        else:
                            UI.show_error("App name cannot be empty.")
                    except (EOFError, KeyboardInterrupt):
                        print("\n")
                        continue
                elif choice == "a" and not alias_set:
                    ConfigManager.add_alias()
                elif choice == "r" and alias_set:
                    ConfigManager.remove_alias()
                elif choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(apps):
                        self.app_manager.run_app(apps[index])
                    else:
                        UI.show_error("Invalid app number.")
                else:
                    UI.show_error("Invalid choice.")
        except Exception as e:
            UI.show_error(f"Unexpected error: {e}")

    def process_command_line(self, args: List[str]) -> None:
        """
        Process command line arguments.

        Args:
            args: Command line arguments.
        """
        if len(args) == 1:
            self.main_menu()
        elif len(args) == 3 and args[1] == "alias":
            if args[2] == "add":
                ConfigManager.add_alias()
            elif args[2] == "remove":
                ConfigManager.remove_alias()
            else:
                UI.show_error("Unknown command. Use 'alias add' or 'alias remove'.")
        else:
            UI.show_message("Usage: python3 main.py [alias add|remove]", color=UI.Color.YELLOW)


def main() -> None:
    """Main entry point for the application."""
    config_tool = ConfigTool()
    config_tool.process_command_line(sys.argv)


if __name__ == "__main__":
    main()