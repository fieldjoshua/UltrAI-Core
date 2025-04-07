#!/usr/bin/env python3
"""
UltraAI Parameter Editor

A command-line interface for viewing and modifying parameters identified by the
parameter glossary generator. This tool allows developers to easily adjust
configurable parameters without manually editing code files.
"""

import os
import re
import json
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import readline  # For better input handling in the terminal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parameter_editor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('parameter_editor')

# Set up paths
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
glossary_dir = script_dir / "parameter_glossary"
glossary_file = glossary_dir / "parameters.json"

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_glossary() -> Dict[str, Any]:
    """Load the parameter glossary from the JSON file"""
    try:
        if not glossary_file.exists():
            logger.error(f"Glossary file not found: {glossary_file}")
            print(f"{Colors.RED}Error: Glossary file not found at {glossary_file}{Colors.ENDC}")
            print(f"Run 'python parameter_glossary_generator.py' first to generate the glossary.")
            sys.exit(1)
            
        with open(glossary_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading glossary: {e}")
        print(f"{Colors.RED}Error loading glossary: {e}{Colors.ENDC}")
        sys.exit(1)

def save_changes(changes: List[Dict[str, Any]]) -> bool:
    """Apply parameter changes to the actual files"""
    if not changes:
        return True
        
    success_count = 0
    failure_count = 0
    
    for change in changes:
        file_path = change['file_path']
        param_name = change['name']
        old_value = change['old_value']
        new_value = change['new_value']
        
        full_path = project_root / file_path
        
        try:
            # Read the file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Convert new_value to proper Python format
            if new_value.lower() == 'true':
                formatted_new_value = 'True'
            elif new_value.lower() == 'false':
                formatted_new_value = 'False'
            elif new_value.isdigit():
                formatted_new_value = new_value
            elif re.match(r"^\d+\.\d+$", new_value):
                formatted_new_value = new_value
            else:
                # Assume it's a string, add quotes
                formatted_new_value = f'"{new_value}"'
                
            # Get the simple name (without class prefix) for regex matching
            simple_name = param_name.split('.')[-1]
            
            # Try different patterns to replace the parameter value
            patterns = [
                # For regular constants: NAME = value
                re.compile(f"({simple_name}\s*=\s*)(.*?)(\s*(?:#|$|\n))", re.MULTILINE),
                # For os.environ.get calls: os.environ.get("NAME", "default")
                re.compile(f'(os\\.environ\\.get\\(["\']\\s*{simple_name}\\s*["\'],\\s*(?:["\'])?)(.*?)(["\']?\\s*\\))', re.MULTILINE),
                # For os.getenv calls: os.getenv("NAME", "default")
                re.compile(f'(os\\.getenv\\(["\']\\s*{simple_name}\\s*["\'],\\s*(?:["\'])?)(.*?)(["\']?\\s*\\))', re.MULTILINE),
                # For class variables: self.NAME = value
                re.compile(f"(self\\.{simple_name}\\s*=\\s*)(.*?)(\s*(?:#|$|\n))", re.MULTILINE)
            ]
            
            original_content = content
            replaced = False
            
            for pattern in patterns:
                if pattern.search(content):
                    content = pattern.sub(f"\\g<1>{formatted_new_value}\\g<3>", content)
                    replaced = True
                    break
            
            if not replaced:
                logger.warning(f"Could not find pattern to replace {param_name} in {file_path}")
                print(f"{Colors.YELLOW}Warning: Could not find pattern to replace {param_name} in {file_path}{Colors.ENDC}")
                failure_count += 1
                continue
                
            # Only write if content changed
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                success_count += 1
                logger.info(f"Updated {param_name} in {file_path}")
            else:
                logger.warning(f"No changes made to {file_path} for {param_name}")
                failure_count += 1
                
        except Exception as e:
            logger.error(f"Error updating {param_name} in {file_path}: {e}")
            print(f"{Colors.RED}Error updating {param_name} in {file_path}: {e}{Colors.ENDC}")
            failure_count += 1
    
    print(f"\n{Colors.GREEN}Successfully applied {success_count} changes{Colors.ENDC}")
    if failure_count > 0:
        print(f"{Colors.YELLOW}{failure_count} changes failed (see log for details){Colors.ENDC}")
    
    return success_count > 0

def filter_parameters(glossary: Dict[str, Any], search_term: str) -> List[Dict[str, Any]]:
    """Filter parameters based on a search term"""
    results = []
    
    search_term = search_term.lower()
    
    for file_path, file_data in glossary.get('files', {}).items():
        for param in file_data.get('parameters', []):
            name = param.get('name', '').lower()
            doc = param.get('doc_string', '').lower()
            value = str(param.get('value', '')).lower()
            
            if search_term in name or search_term in doc or search_term in value:
                param['file_path'] = file_path  # Add file path to each parameter
                results.append(param)
    
    return results

def print_parameter_table(parameters: List[Dict[str, Any]], title: str = "Parameters"):
    """Print a formatted table of parameters"""
    if not parameters:
        print(f"\n{Colors.YELLOW}No parameters found.{Colors.ENDC}")
        return
        
    # Calculate column widths
    name_width = max(max(len(p.get('name', '')) for p in parameters), 20)
    value_width = max(max(len(str(p.get('value', ''))) for p in parameters), 15)
    type_width = max(max(len(p.get('data_type', '')) for p in parameters), 10)
    path_width = min(max(max(len(p.get('file_path', '')) for p in parameters), 25), 40)
    
    # Print the table header
    print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * (name_width + value_width + type_width + path_width + 13)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Name':<{name_width}}  {'Value':<{value_width}}  {'Type':<{type_width}}  {'File':<{path_width}}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * (name_width + value_width + type_width + path_width + 13)}{Colors.ENDC}")
    
    # Print each parameter row
    for i, param in enumerate(parameters):
        name = param.get('name', '')
        value = str(param.get('value', ''))
        param_type = param.get('data_type', '')
        file_path = param.get('file_path', '')
        
        # Truncate file path if too long
        if len(file_path) > path_width:
            file_path = "..." + file_path[-(path_width-3):]
            
        print(f"{Colors.BOLD if i % 2 == 0 else ''}{name:<{name_width}}  {value:<{value_width}}  {param_type:<{type_width}}  {file_path:<{path_width}}{Colors.ENDC}")
    
    print(f"{Colors.CYAN}{'-' * (name_width + value_width + type_width + path_width + 13)}{Colors.ENDC}")
    print(f"Total: {len(parameters)} parameters\n")

def print_parameter_details(param: Dict[str, Any]):
    """Print detailed information about a parameter"""
    name = param.get('name', '')
    value = param.get('value', '')
    param_type = param.get('parameter_type', '')
    data_type = param.get('data_type', '')
    file_path = param.get('file_path', '')
    line_number = param.get('line_number', '')
    doc_string = param.get('doc_string', '')
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}Parameter Details:{Colors.ENDC}")
    print(f"{Colors.BOLD}Name:{Colors.ENDC}        {name}")
    print(f"{Colors.BOLD}Value:{Colors.ENDC}       {value}")
    print(f"{Colors.BOLD}Type:{Colors.ENDC}        {data_type}")
    print(f"{Colors.BOLD}Category:{Colors.ENDC}    {param_type}")
    print(f"{Colors.BOLD}File:{Colors.ENDC}        {file_path}")
    print(f"{Colors.BOLD}Line:{Colors.ENDC}        {line_number}")
    
    if doc_string:
        print(f"{Colors.BOLD}Description:{Colors.ENDC} {doc_string}")
    
    print()

def edit_parameter(param: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Edit a parameter value and return the change if modified"""
    name = param.get('name', '')
    current_value = param.get('value', '')
    data_type = param.get('data_type', '')
    
    print(f"\n{Colors.BOLD}Editing parameter: {Colors.BLUE}{name}{Colors.ENDC}")
    print(f"Current value ({data_type}): {Colors.GREEN}{current_value}{Colors.ENDC}")
    
    new_value = input("Enter new value (or leave empty to cancel): ").strip()
    
    if not new_value:
        return None
        
    # Validate the new value based on data type
    if data_type == "integer":
        try:
            int(new_value)
        except ValueError:
            print(f"{Colors.RED}Error: Value must be an integer{Colors.ENDC}")
            return None
    elif data_type == "float":
        try:
            float(new_value)
        except ValueError:
            print(f"{Colors.RED}Error: Value must be a float{Colors.ENDC}")
            return None
    elif data_type == "boolean":
        if new_value.lower() not in ('true', 'false'):
            print(f"{Colors.RED}Error: Value must be 'True' or 'False'{Colors.ENDC}")
            return None
    
    if new_value == current_value:
        print(f"{Colors.YELLOW}No changes made.{Colors.ENDC}")
        return None
        
    return {
        'name': name,
        'file_path': param.get('file_path', ''),
        'old_value': current_value,
        'new_value': new_value
    }

def browse_parameters_by_file(glossary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Interactive browser for parameters organized by file"""
    changes = []
    files = sorted(glossary.get('files', {}).keys())
    
    if not files:
        print(f"{Colors.YELLOW}No files with parameters found.{Colors.ENDC}")
        return changes
        
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}Parameter Browser - Files{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
        
        for i, file_path in enumerate(files):
            param_count = len(glossary['files'][file_path].get('parameters', []))
            print(f"{i+1:2d}. {file_path} ({param_count} parameters)")
        
        print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
        print("q. Return to main menu")
        
        choice = input("\nSelect a file (number) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            break
            
        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(files):
                file_path = files[file_index]
                file_changes = browse_file_parameters(glossary['files'][file_path], file_path)
                changes.extend(file_changes)
            else:
                print(f"{Colors.RED}Invalid selection. Please try again.{Colors.ENDC}")
                input("Press Enter to continue...")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number or 'q'.{Colors.ENDC}")
            input("Press Enter to continue...")
    
    return changes

def browse_file_parameters(file_data: Dict[str, Any], file_path: str) -> List[Dict[str, Any]]:
    """Browse and edit parameters within a file"""
    changes = []
    parameters = file_data.get('parameters', [])
    
    if not parameters:
        print(f"{Colors.YELLOW}No parameters found in this file.{Colors.ENDC}")
        input("Press Enter to continue...")
        return changes
        
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}File: {file_path}{Colors.ENDC}")
        
        # Add file_path to each parameter
        for param in parameters:
            param['file_path'] = file_path
            
        print_parameter_table(parameters, "Parameters")
        
        print("Options:")
        print("  e<num>  - Edit parameter (e.g., e1 to edit the first parameter)")
        print("  d<num>  - View parameter details (e.g., d2)")
        print("  f       - Filter parameters")
        print("  q       - Return to file selection")
        
        choice = input("\nEnter option: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'f':
            search_term = input("Enter search term: ").strip().lower()
            filtered = [p for p in parameters if 
                       search_term in p.get('name', '').lower() or 
                       search_term in (p.get('doc_string', '') or '').lower()]
            
            if filtered:
                print_parameter_table(filtered, f"Filtered Parameters - '{search_term}'")
            else:
                print(f"{Colors.YELLOW}No matching parameters found.{Colors.ENDC}")
                
            input("Press Enter to continue...")
        elif choice.startswith('e') and choice[1:].isdigit():
            param_index = int(choice[1:]) - 1
            if 0 <= param_index < len(parameters):
                change = edit_parameter(parameters[param_index])
                if change:
                    changes.append(change)
            else:
                print(f"{Colors.RED}Invalid parameter number.{Colors.ENDC}")
                
            input("Press Enter to continue...")
        elif choice.startswith('d') and choice[1:].isdigit():
            param_index = int(choice[1:]) - 1
            if 0 <= param_index < len(parameters):
                print_parameter_details(parameters[param_index])
            else:
                print(f"{Colors.RED}Invalid parameter number.{Colors.ENDC}")
                
            input("Press Enter to continue...")
        else:
            print(f"{Colors.RED}Invalid option. Please try again.{Colors.ENDC}")
            input("Press Enter to continue...")
    
    return changes

def browse_parameters_by_category(glossary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Interactive browser for parameters organized by category"""
    changes = []
    categories = {
        'Environment Variables': glossary.get('categories', {}).get('environment_variables', []),
        'Constants': glossary.get('categories', {}).get('constants', []),
        'Class Constants': glossary.get('categories', {}).get('class_constants', [])
    }
    
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}Parameter Browser - Categories{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
        
        category_names = list(categories.keys())
        for i, category_name in enumerate(category_names):
            param_count = len(categories[category_name])
            print(f"{i+1:2d}. {category_name} ({param_count} parameters)")
        
        print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
        print("q. Return to main menu")
        
        choice = input("\nSelect a category (number) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            break
            
        try:
            category_index = int(choice) - 1
            if 0 <= category_index < len(category_names):
                category_name = category_names[category_index]
                category_changes = browse_category_parameters(categories[category_name], category_name)
                changes.extend(category_changes)
            else:
                print(f"{Colors.RED}Invalid selection. Please try again.{Colors.ENDC}")
                input("Press Enter to continue...")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number or 'q'.{Colors.ENDC}")
            input("Press Enter to continue...")
    
    return changes

def browse_category_parameters(parameters: List[Dict[str, Any]], category_name: str) -> List[Dict[str, Any]]:
    """Browse and edit parameters within a category"""
    changes = []
    
    if not parameters:
        print(f"{Colors.YELLOW}No parameters found in this category.{Colors.ENDC}")
        input("Press Enter to continue...")
        return changes
        
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}Category: {category_name}{Colors.ENDC}")
        
        print_parameter_table(parameters, "Parameters")
        
        print("Options:")
        print("  e<num>  - Edit parameter (e.g., e1 to edit the first parameter)")
        print("  d<num>  - View parameter details (e.g., d2)")
        print("  f       - Filter parameters")
        print("  q       - Return to category selection")
        
        choice = input("\nEnter option: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'f':
            search_term = input("Enter search term: ").strip().lower()
            filtered = [p for p in parameters if 
                       search_term in p.get('name', '').lower() or 
                       search_term in (p.get('doc_string', '') or '').lower()]
            
            if filtered:
                print_parameter_table(filtered, f"Filtered Parameters - '{search_term}'")
            else:
                print(f"{Colors.YELLOW}No matching parameters found.{Colors.ENDC}")
                
            input("Press Enter to continue...")
        elif choice.startswith('e') and choice[1:].isdigit():
            param_index = int(choice[1:]) - 1
            if 0 <= param_index < len(parameters):
                change = edit_parameter(parameters[param_index])
                if change:
                    changes.append(change)
            else:
                print(f"{Colors.RED}Invalid parameter number.{Colors.ENDC}")
                
            input("Press Enter to continue...")
        elif choice.startswith('d') and choice[1:].isdigit():
            param_index = int(choice[1:]) - 1
            if 0 <= param_index < len(parameters):
                print_parameter_details(parameters[param_index])
            else:
                print(f"{Colors.RED}Invalid parameter number.{Colors.ENDC}")
                
            input("Press Enter to continue...")
        else:
            print(f"{Colors.RED}Invalid option. Please try again.{Colors.ENDC}")
            input("Press Enter to continue...")
    
    return changes

def search_parameters(glossary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search for parameters and edit them"""
    changes = []
    
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}Parameter Search{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
        
        search_term = input("Enter search term (or 'q' to return to menu): ").strip()
        
        if search_term.lower() == 'q':
            break
            
        results = filter_parameters(glossary, search_term)
        
        if not results:
            print(f"{Colors.YELLOW}No parameters found matching '{search_term}'.{Colors.ENDC}")
            input("Press Enter to continue...")
            continue
            
        print_parameter_table(results, f"Search Results - '{search_term}'")
        
        while True:
            print("\nOptions:")
            print("  e<num>  - Edit parameter (e.g., e1 to edit the first parameter)")
            print("  d<num>  - View parameter details (e.g., d2)")
            print("  n       - New search")
            print("  q       - Return to main menu")
            
            choice = input("\nEnter option: ").strip().lower()
            
            if choice == 'q':
                return changes
            elif choice == 'n':
                break
            elif choice.startswith('e') and choice[1:].isdigit():
                param_index = int(choice[1:]) - 1
                if 0 <= param_index < len(results):
                    change = edit_parameter(results[param_index])
                    if change:
                        changes.append(change)
                else:
                    print(f"{Colors.RED}Invalid parameter number.{Colors.ENDC}")
                    
                input("Press Enter to continue...")
            elif choice.startswith('d') and choice[1:].isdigit():
                param_index = int(choice[1:]) - 1
                if 0 <= param_index < len(results):
                    print_parameter_details(results[param_index])
                else:
                    print(f"{Colors.RED}Invalid parameter number.{Colors.ENDC}")
                    
                input("Press Enter to continue...")
            else:
                print(f"{Colors.RED}Invalid option. Please try again.{Colors.ENDC}")
    
    return changes

def show_main_menu():
    """Display the main menu"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}UltraAI Parameter Editor{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
    print("1. Browse parameters by file")
    print("2. Browse parameters by category")
    print("3. Search parameters")
    print("4. Generate new parameter glossary")
    print("q. Quit")
    print(f"{Colors.CYAN}{'-' * 80}{Colors.ENDC}")
    
    return input("Select an option: ").strip().lower()

def generate_new_glossary():
    """Generate a new parameter glossary by running the generator script"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}Generating new parameter glossary...{Colors.ENDC}")
    
    generator_path = script_dir / "parameter_glossary_generator.py"
    if not generator_path.exists():
        print(f"{Colors.RED}Error: Generator script not found at {generator_path}{Colors.ENDC}")
        return False
        
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(generator_path)], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}Parameter glossary generated successfully.{Colors.ENDC}")
            print(result.stdout)
            return True
        else:
            print(f"{Colors.RED}Error generating parameter glossary:{Colors.ENDC}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"{Colors.RED}Error running generator script: {e}{Colors.ENDC}")
        return False

def main():
    """Main function to run the parameter editor"""
    parser = argparse.ArgumentParser(description="UltraAI Parameter Editor")
    parser.add_argument("--search", "-s", help="Search for parameters matching the given term")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate a new parameter glossary before starting")
    args = parser.parse_args()
    
    # Generate new glossary if requested
    if args.generate:
        if not generate_new_glossary():
            input("Press Enter to continue...")
    
    # Load the parameter glossary
    glossary = load_glossary()
    
    changes = []
    
    # If search term provided, go directly to search results
    if args.search:
        results = filter_parameters(glossary, args.search)
        if results:
            print_parameter_table(results, f"Search Results - '{args.search}'")
        else:
            print(f"{Colors.YELLOW}No parameters found matching '{args.search}'.{Colors.ENDC}")
        return
    
    # Main menu loop
    while True:
        choice = show_main_menu()
        
        if choice == 'q':
            if changes:
                print(f"\n{Colors.YELLOW}You have {len(changes)} unsaved changes.{Colors.ENDC}")
                save = input("Save changes before quitting? (y/n): ").strip().lower()
                if save == 'y':
                    save_changes(changes)
            break
        elif choice == '1':
            file_changes = browse_parameters_by_file(glossary)
            changes.extend(file_changes)
        elif choice == '2':
            category_changes = browse_parameters_by_category(glossary)
            changes.extend(category_changes)
        elif choice == '3':
            search_changes = search_parameters(glossary)
            changes.extend(search_changes)
        elif choice == '4':
            if generate_new_glossary():
                # Reload the glossary after generating
                glossary = load_glossary()
            input("Press Enter to continue...")
        else:
            print(f"{Colors.RED}Invalid option. Please try again.{Colors.ENDC}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        print("See parameter_editor.log for details.") 