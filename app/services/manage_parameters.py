#!/usr/bin/env python3
"""
UltraAI Parameter Management

A launcher script that provides easy access to all parameter management tools.
This script detects if the parameter glossary exists and guides the user through
the setup process if needed.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Set up paths
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
glossary_dir = script_dir / "parameter_glossary"
glossary_file = glossary_dir / "parameters.json"
generator_file = script_dir / "parameter_glossary_generator.py"
editor_file = script_dir / "parameter_editor.py"


# ANSI colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def check_environment():
    """Check if all required files exist and create directories if needed"""
    # Create glossary directory if it doesn't exist
    if not glossary_dir.exists():
        print(f"{Colors.YELLOW}Creating parameter glossary directory...{Colors.ENDC}")
        glossary_dir.mkdir(exist_ok=True)

    # Check if required files exist
    missing_files = []
    if not generator_file.exists():
        missing_files.append(str(generator_file))
    if not editor_file.exists():
        missing_files.append(str(editor_file))

    if missing_files:
        print(
            f"{Colors.RED}Error: The following required files are missing:{Colors.ENDC}"
        )
        for file in missing_files:
            print(f"  - {file}")
        print(
            "\nPlease make sure all parameter management scripts are properly installed."
        )
        return False

    return True


def generate_glossary():
    """Generate the parameter glossary by running the generator script"""
    print(f"{Colors.BOLD}{Colors.BLUE}Generating parameter glossary...{Colors.ENDC}")

    try:
        result = subprocess.run(
            [sys.executable, str(generator_file)], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(
                f"{Colors.GREEN}Parameter glossary generated successfully.{Colors.ENDC}"
            )
            return True
        else:
            print(f"{Colors.RED}Error generating parameter glossary:{Colors.ENDC}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"{Colors.RED}Error running generator script: {e}{Colors.ENDC}")
        return False


def launch_editor(args=None):
    """Launch the parameter editor with optional arguments"""
    cmd = [sys.executable, str(editor_file)]
    if args:
        cmd.extend(args)

    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"{Colors.RED}Error launching parameter editor: {e}{Colors.ENDC}")
        return False

    return True


def show_menu():
    """Display the main menu and get user choice"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}UltraAI Parameter Management{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")

    if glossary_file.exists():
        print("1. Browse and edit parameters")
        print("2. Regenerate parameter glossary")
        print("3. Search parameters")
    else:
        print(
            f"{Colors.YELLOW}No parameter glossary found. You need to generate one first.{Colors.ENDC}"
        )
        print("1. Generate parameter glossary")

    print("q. Quit")
    print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")

    return input("Select an option: ").strip().lower()


def main():
    """Main function to run the parameter management launcher"""
    parser = argparse.ArgumentParser(description="UltraAI Parameter Management")
    parser.add_argument(
        "--generate",
        "-g",
        action="store_true",
        help="Generate parameter glossary and exit",
    )
    parser.add_argument(
        "--edit", "-e", action="store_true", help="Launch parameter editor directly"
    )
    parser.add_argument(
        "--search", "-s", help="Search for parameters matching the given term"
    )
    args = parser.parse_args()

    # Check environment
    if not check_environment():
        return 1

    # Handle command-line arguments
    if args.generate:
        return 0 if generate_glossary() else 1
    elif args.edit:
        if not glossary_file.exists():
            print(
                f"{Colors.YELLOW}Parameter glossary not found. Generating now...{Colors.ENDC}"
            )
            if not generate_glossary():
                return 1

        return 0 if launch_editor() else 1
    elif args.search:
        if not glossary_file.exists():
            print(
                f"{Colors.YELLOW}Parameter glossary not found. Generating now...{Colors.ENDC}"
            )
            if not generate_glossary():
                return 1

        return 0 if launch_editor(["--search", args.search]) else 1

    # Interactive menu mode
    while True:
        choice = show_menu()

        if choice == "q":
            break
        elif glossary_file.exists():
            if choice == "1":
                launch_editor()
            elif choice == "2":
                generate_glossary()
                input("Press Enter to continue...")
            elif choice == "3":
                search_term = input("Enter search term: ").strip()
                if search_term:
                    launch_editor(["--search", search_term])
            else:
                print(f"{Colors.RED}Invalid option. Please try again.{Colors.ENDC}")
                input("Press Enter to continue...")
        else:
            if choice == "1":
                if generate_glossary():
                    print(
                        f"{Colors.GREEN}Parameter glossary generated. You can now browse parameters.{Colors.ENDC}"
                    )
                    input("Press Enter to continue...")
            else:
                print(f"{Colors.RED}Invalid option. Please try again.{Colors.ENDC}")
                input("Press Enter to continue...")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
