import sys

from apps.config.config_tool import ConfigTool

def main() -> None:
    """Main entry point for the application."""
    config_tool = ConfigTool()
    config_tool.process_command_line(sys.argv)

if __name__ == "__main__":
    main()