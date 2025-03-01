import os
import sys
import subprocess
from typing import List

from apps.config.ui import UI

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