import os
import sys
import platform
import subprocess
from typing import List

# Placeholder for apps.config.ui (assumed implementation)
class UI:
    class Color:
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        RESET = "\033[0m"
        RED = "\033[91m"

    class Style:
        SEPARATOR_MARKER = "─" * 40

    @staticmethod
    def show_message(message: str, color: str = None) -> None:
        if color:
            print(f"{color}{message}{UI.Color.RESET}")
        else:
            print(message)

    @staticmethod
    def show_error(message: str) -> None:
        print(f"{UI.Color.RED}Error: {message}{UI.Color.RESET}")

    @staticmethod
    def draw_box(content: List[str], center_title: bool = True, title_color: str = None) -> None:
        # Simple box drawing (assumed behavior)
        max_width = max(len(line) for line in content) + 4
        border = "═" * (max_width - 2)
        print(f"╔{border}╗")
        for i, line in enumerate(content):
            if i == 0 and center_title:
                line = line.center(max_width - 4)
            if i == 0 and title_color:
                line = f"{title_color}{line}{UI.Color.RESET}"
            print(f"║ {line:<{max_width - 4}} ║")
        print(f"╚{border}╝")

    @staticmethod
    def get_input(prompt: str) -> str:
        return input(prompt)


class ConfigManager:
    """Class for managing shell configuration and aliases."""

    MARKER_START = "# Config tool alias - do not edit\n"
    MARKER_END = "# End config tool alias\n"

    @staticmethod
    def get_shell_config_file() -> str:
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


class AppManager:
    """Class for managing apps in the config tool."""

    def __init__(self, apps_dir: str):
        self.apps_dir = apps_dir
        self._ensure_apps_dir()

    def _ensure_apps_dir(self) -> None:
        if not os.path.exists(self.apps_dir):
            try:
                os.makedirs(self.apps_dir)
                UI.show_message("Created /apps directory.", color=UI.Color.YELLOW)
            except OSError as e:
                UI.show_error(f"Creating apps directory: {e}")

    def list_apps(self) -> List[str]:
        if not os.path.exists(self.apps_dir):
            return []
        try:
            all_dirs = [
                d for d in os.listdir(self.apps_dir)
                if os.path.isdir(os.path.join(self.apps_dir, d)) and d != "config"
            ]
            app_dirs = [d for d in all_dirs if d.startswith('[') and d.endswith(']')]
            return [d[1:-1] for d in app_dirs]
        except OSError as e:
            UI.show_error(f"Listing apps: {e}")
            return []

    def run_app(self, app_name: str) -> None:
        dir_name = f"[{app_name}]"
        app_dir = os.path.join(self.apps_dir, dir_name)
        app_path = os.path.join(app_dir, "main.py")

        # Check for sub-apps
        sub_apps = []
        try:
            for item in os.listdir(app_dir):
                item_path = os.path.join(app_dir, item)
                if os.path.isdir(item_path) and item.startswith('[') and item.endswith(']'):
                    sub_apps.append(item[1:-1])
        except OSError:
            sub_apps = []

        if sub_apps:
            while True:
                content = [f"App: {app_name}", UI.Style.SEPARATOR_MARKER]
                if os.path.exists(app_path):
                    content.append("1. Run this app")
                    content.append(UI.Style.SEPARATOR_MARKER)
                offset = 2 if os.path.exists(app_path) else 1
                for i, sub_app in enumerate(sub_apps, offset):
                    content.append(f"{i}. {sub_app}")
                content.append(UI.Style.SEPARATOR_MARKER)
                content.append("b. Back to main menu")
                content.append("q. Quit")

                UI.draw_box(content, center_title=True, title_color=UI.Color.YELLOW)
                choice = UI.get_input(prompt="Select an option: ")

                if choice == "b":
                    return
                elif choice == "q":
                    sys.exit(0)
                elif choice == "1" and os.path.exists(app_path):
                    break
                elif choice.isdigit():
                    index = int(choice) - offset
                    if 0 <= index < len(sub_apps):
                        original_apps_dir = self.apps_dir
                        try:
                            self.apps_dir = os.path.join(self.apps_dir, dir_name)
                            self.run_app(sub_apps[index])
                        finally:
                            self.apps_dir = original_apps_dir
                        return
                    else:
                        UI.show_error("Invalid sub-app number.")
                else:
                    UI.show_error("Invalid choice.")

        if not os.path.exists(app_path):
            UI.show_error(f"App '{app_name}' does not have a main.py file.")
            return

        try:
            UI.show_message(f"Running app: {app_name}", color=UI.Color.CYAN)
            result = subprocess.run([sys.executable, app_path], capture_output=True, text=True, check=True)
            if result.stdout:
                UI.show_message(f"App Output:\n{result.stdout}", color=UI.Color.GREEN)
            if result.stderr:
                UI.show_error(f"Errors:\n{result.stderr}")
            UI.show_message(f"App '{app_name}' finished", color=UI.Color.GREEN)

            # Add "press to continue" feature
            input(f"{UI.Color.YELLOW}Press Enter to continue...{UI.Color.RESET}")
        except subprocess.SubprocessError as e:
            UI.show_error(f"Running app '{app_name}': {e}")
            # Also add "press to continue" after error
            input(f"{UI.Color.YELLOW}Press Enter to continue...{UI.Color.RESET}")

    def create_sample_app(self, app_name: str) -> None:
        folder_name = f"[{app_name}]"
        app_path = os.path.join(self.apps_dir, folder_name)
        if os.path.exists(app_path):
            UI.show_error(f"App '{app_name}' already exists.")
            return
        try:
            os.makedirs(app_path)
            self._create_main_py(app_path, app_name)
            UI.show_message(f"Sample app '{app_name}' created in /apps.", color=UI.Color.GREEN)
        except OSError as e:
            UI.show_error(f"Creating app: {e}")

    def _create_main_py(self, app_path: str, app_name: str) -> None:
        sample_code = (
            f'def main():\n'
            f'    print("Hello from {app_name}!")\n\n'
            f'if __name__ == "__main__":\n'
            f'    main()\n'
        )
        with open(os.path.join(app_path, "main.py"), "w") as f:
            f.write(sample_code)


class ConfigTool:
    """Main class for the configuration tool."""

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        apps_dir = os.path.join(script_dir, "apps")
        self.app_manager = AppManager(apps_dir)

    def build_menu_content(self, apps: List[str], alias_set: bool) -> List[str]:
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
    config_tool = ConfigTool()
    config_tool.process_command_line(sys.argv)


if __name__ == "__main__":
    main()