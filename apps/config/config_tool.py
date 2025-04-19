import sys
import argparse
from typing import List
from pathlib import Path

from apps.config.app_manager import AppManager
from apps.config.ui import UI
from apps.config.config_manager import ConfigManager

class ConfigTool:
    """Main class for the configuration tool."""

    def __init__(self):
        # Determine project root and apps directory using pathlib
        project_root = Path(__file__).resolve().parents[2]
        apps_dir = project_root / "apps"
        self.app_manager = AppManager(str(apps_dir))

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
        # Move sample app creation and alias management under Settings
        content.append("s. Settings")
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
                elif choice == "s":
                    # Enter Settings menu for alias and sample app management
                    self.settings_menu()
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

    def settings_menu(self) -> None:
        """Display settings menu for alias and sample app management."""
        try:
            while True:
                # Refresh alias state for each display
                config_file = ConfigManager.get_shell_config_file()
                alias_set = ConfigManager.is_alias_set(config_file)
                content = ["Settings", UI.Style.SEPARATOR_MARKER]
                content.append("Options:")
                content.append("n. Create new sample app")
                content.append("r. Remove alias 'dagger'" if alias_set else "a. Add alias 'dagger'")
                content.append("b. Back to main menu")
                UI.draw_box(content, center_title=True, title_color=UI.Color.YELLOW)

                choice = UI.get_input(prompt="> ")
                if choice == "b":
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
                else:
                    UI.show_error("Invalid choice.")
        except Exception as e:
            UI.show_error(f"Unexpected error: {e}")

    def process_command_line(self, argv: List[str]) -> None:
        """
        Parse and dispatch command line arguments using argparse.
        """
        parser = argparse.ArgumentParser(prog='dagger',
                                         description='Dagger configuration tool')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Interactive menu (default)
        subparsers.add_parser('menu', help='Interactive menu (default)')

        # Alias management
        alias_parser = subparsers.add_parser('alias', help='Manage dagger alias')
        alias_sub = alias_parser.add_subparsers(dest='action', help='Alias actions')
        alias_sub.add_parser('add', help='Add alias')
        alias_sub.add_parser('remove', help='Remove alias')

        # Create a new sample app
        new_parser = subparsers.add_parser('new', help='Create new sample app')
        new_parser.add_argument('name', help='Name of the new app')

        # Run an existing app
        run_parser = subparsers.add_parser('run', help='Run an app')
        run_parser.add_argument('name', help='Name of the app to run')

        # List available apps
        subparsers.add_parser('list', help='List available apps')

        args = parser.parse_args(argv[1:])

        # Dispatch commands
        if args.command is None or args.command == 'menu':
            self.main_menu()
        elif args.command == 'alias':
            if args.action == 'add':
                ConfigManager.add_alias()
            elif args.action == 'remove':
                ConfigManager.remove_alias()
            else:
                parser.error("alias command requires 'add' or 'remove'.")
        elif args.command == 'new':
            self.app_manager.create_sample_app(args.name)
        elif args.command == 'run':
            self.app_manager.run_app(args.name)
        elif args.command == 'list':
            apps = self.app_manager.list_apps()
            if apps:
                content = ['Available Apps:'] + [f"{i}. {app}" for i, app in enumerate(apps, 1)]
                UI.draw_box(content, center_title=False, title_color=UI.Color.BLUE)
            else:
                UI.show_message("No apps available.", color=UI.Color.YELLOW)
        else:
            parser.print_help()