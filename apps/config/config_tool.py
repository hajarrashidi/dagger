import sys
from typing import List

from apps.config.app_manager import AppManager
from apps.config.ui import UI
from apps.config.config_manager import ConfigManager

class ConfigTool:
    """Main class for the configuration tool."""

    def __init__(self):
        import os
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        apps_dir = os.path.join(script_dir, "apps")
        self.app_manager = AppManager(apps_dir)

    def build_menu_content(self, apps: List[str], alias_set: bool) -> List[str]:
        """
        Build the content list for the main menu.

        Args:
            apps: List of available app names.
            alias_set: Whether the 'dagger' alias is set.

        Returns:
            Lines for the menu, including title and separators.
        """
        content = ["Dagger", UI.Style.SEPARATOR_MARKER]
        if apps:
            content.append("Available Apps:")
            for i, app in enumerate(apps, 1):
                content.append(f"{i}. {app}")
        else:
            content.append("No apps available yet.")
        content.append(UI.Style.SEPARATOR_MARKER)
        content.append("Options:")
        content.append("n. Create new sample app")
        content.append("r. Remove alias 'dagger'" if alias_set else "a. Add alias 'dagger'")
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