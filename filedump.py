#!/usr/bin/env python3
"""
FileDump - An utility to extract all the files from a specified directory with optional filtering.

Usage:
    python filedump.py source_directory [destination_directory] [--filter PATTERN]
    python filedump.py svd                  # List all saved projects
    python filedump.py svd NAME             # Run a saved project
    python filedump.py svd save NAME        # Save current args as a project
    python filedump.py svd create           # Create a project step by step
    python filedump.py svd edit NAME        # Edit a saved project
    python filedump.py svd delete NAME      # Delete a saved project

Arguments:
    source_directory     - The directory to extract files from (required)
    destination_directory - Where to save the extracted files (optional, defaults to current directory)
    --filter PATTERN     - Only include files matching this pattern (optional, supports glob patterns)
    --flat               - Don't preserve directory structure, copy all files to the destination root

Examples:
    python filedump.py ~/projects/my-mod
    python filedump.py ~/projects/my-mod ./backup
    python filedump.py ~/projects/my-mod ./backup --filter "*.java"
    python filedump.py svd save my-mod-project
    python filedump.py svd my-mod-project
"""

import os
import sys
import json
import shutil
import glob
import argparse
from pathlib import Path


# Config file path - use a file in the same directory as the script for portability
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "filedump_projects.json")


def load_projects():
    """Load saved projects from config file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Info: Config file does not exist yet: {CONFIG_FILE}")
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            print(f"Successfully loaded projects from: {CONFIG_FILE}")
            return data
    except json.JSONDecodeError:
        print(f"Warning: Config file exists but contains invalid JSON: {CONFIG_FILE}")
        return {}
    except IOError as e:
        print(f"Warning: Could not read config file {CONFIG_FILE}: {e}")
        return {}


def save_projects(projects):
    """Save projects to config file."""
    try:
        # Make sure we're saving a valid JSON structure
        if not isinstance(projects, dict):
            print(f"Error: Projects data is not a dictionary: {type(projects)}")
            return False
            
        # Create directory if needed
        config_dir = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(config_dir) and config_dir:
            os.makedirs(config_dir)
            
        # Write with error handling and debug info
        with open(CONFIG_FILE, 'w') as f:
            json.dump(projects, f, indent=2)
            
        print(f"Project data saved to: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error: Could not save config file: {e}")
        print(f"Attempted to save to: {CONFIG_FILE}")
        return False


def list_saved_projects():
    """List all saved projects."""
    projects = load_projects()

    if not projects:
        print("No saved projects found.")
        return

    print("Saved Projects:")
    for name, config in projects.items():
        filter_txt = f" (filter: {config['filter']})" if config.get('filter') else ""
        structure_txt = "" if config.get('preserve_structure', True) else " (flat structure)"
        print(f"  - {name}: {config['origin']} → {config['dest']}{filter_txt}{structure_txt}")


def save_project(name, origin, dest, filter_pattern=None, preserve_structure=True):
    """Save a project configuration."""
    projects = load_projects()

    # Create project config
    projects[name] = {
        "origin": origin,
        "dest": dest,
        "filter": filter_pattern,
        "preserve_structure": preserve_structure
    }

    save_projects(projects)
    print(f"Project '{name}' saved successfully.")


def create_project_interactive():
    """Create a new project interactively."""
    print("Create a New Project")
    print("===================")
    
    # Get project details
    while True:
        name = input("Project name: ").strip()
        if not name:
            print("Error: Project name cannot be empty.")
            continue
            
        # Replace spaces with hyphens
        name = name.replace(" ", "-")
        print(f"Using project name: {name}")
            
        # Check if project already exists
        projects = load_projects()
        if name in projects:
            overwrite = input(f"Project '{name}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                continue
        
        break
    
    # Get source directory
    while True:
        origin = input("Source directory: ").strip()
        if not origin:
            print("Error: Source directory cannot be empty.")
            continue
            
        # Expand user directory if needed
        origin = os.path.expanduser(origin)
        
        if not os.path.isdir(origin):
            create_dir = input("Directory doesn't exist. Create it? (y/n): ").strip().lower()
            if create_dir == 'y':
                try:
                    os.makedirs(origin)
                except OSError as e:
                    print(f"Error creating directory: {e}")
                    continue
            else:
                continue
                
        break
    
    # Get destination directory
    while True:
        dest = input("Destination directory [current directory]: ").strip()
        if not dest:
            dest = os.getcwd()
            
        # Expand user directory if needed
        dest = os.path.expanduser(dest)
        
        if not os.path.isdir(dest):
            create_dir = input("Directory doesn't exist. Create it? (y/n): ").strip().lower()
            if create_dir == 'y':
                try:
                    os.makedirs(dest)
                except OSError as e:
                    print(f"Error creating directory: {e}")
                    continue
            else:
                continue
                
        break
    
    # Get filter pattern
    filter_pattern = input("Filter pattern (e.g., *.java) [optional]: ").strip()
    if not filter_pattern:
        filter_pattern = None
    
    # Get more options
    preserve_structure = input("Preserve directory structure? (y/n) [y]: ").strip().lower()
    preserve_structure = preserve_structure != 'n'  # Default to yes
    
    # Save the project with additional options
    save_project(name, origin, dest, filter_pattern, preserve_structure)
    
    print(f"\nProject '{name}' created successfully!")
    print(f"You can run it using: filedump svd {name}")


def edit_project(name):
    """Edit a saved project interactively."""
    projects = load_projects()
    
    if name not in projects:
        print(f"Error: Project '{name}' does not exist.")
        return
    
    project = projects[name]
    
    # Show current values
    print(f"Editing project '{name}':")
    print(f"  Current source directory: {project['origin']}")
    print(f"  Current destination directory: {project['dest']}")
    print(f"  Current filter pattern: {project.get('filter', 'None')}")
    print(f"  Preserve directory structure: {project.get('preserve_structure', True)}")
    
    # Get new values
    print("\nEnter new values (leave empty to keep current value):")
    new_origin = input("New source directory: ").strip()
    new_dest = input("New destination directory: ").strip()
    new_filter = input("New filter pattern: ").strip()
    new_preserve = input("Preserve directory structure? (y/n): ").strip()
    
    # Update project
    if new_origin:
        project['origin'] = new_origin
    if new_dest:
        project['dest'] = new_dest
    if new_filter:
        project['filter'] = new_filter
    elif new_filter == "None" or new_filter == "none":
        project['filter'] = None
    if new_preserve.lower() in ('y', 'n'):
        project['preserve_structure'] = (new_preserve.lower() == 'y')
    
    save_projects(projects)
    print(f"Project '{name}' updated successfully.")


def delete_project(name):
    """Delete a saved project."""
    projects = load_projects()
    
    if name not in projects:
        print(f"Error: Project '{name}' does not exist.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete project '{name}'? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
    
    # Delete project
    del projects[name]
    save_projects(projects)
    print(f"Project '{name}' deleted successfully.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract files from a directory with optional filtering.")
    
    # Handle svd command specially
    if len(sys.argv) > 1 and sys.argv[1] == "svd":
        # Remove the 'svd' argument
        sys.argv.pop(1)
        
        # Handle various svd commands
        if len(sys.argv) == 1:
            # Just 'svd' with no other args - list projects
            list_saved_projects()
            sys.exit(0)
        elif len(sys.argv) >= 2:
            if sys.argv[1] == "save" and len(sys.argv) >= 3:
                # Check if we have enough args to save
                if len(sys.argv) < 5:
                    print("Error: To save a project, you need to provide source and destination directories.")
                    print("Usage: filedump svd save PROJECT_NAME SOURCE DEST [--filter PATTERN]")
                    sys.exit(1)
                
                project_name = sys.argv[2]
                source = sys.argv[3]
                dest = sys.argv[4]
                
                # Check for filter argument
                filter_pattern = None
                if "--filter" in sys.argv:
                    filter_idx = sys.argv.index("--filter")
                    if filter_idx + 1 < len(sys.argv):
                        filter_pattern = sys.argv[filter_idx + 1]
                
                save_project(project_name, source, dest, filter_pattern)
                sys.exit(0)
            elif sys.argv[1] == "create":
                create_project_interactive()
                sys.exit(0)
            elif sys.argv[1] == "edit" and len(sys.argv) >= 3:
                project_name = sys.argv[2]
                edit_project(project_name)
                sys.exit(0)
            elif sys.argv[1] == "delete" and len(sys.argv) >= 3:
                project_name = sys.argv[2]
                delete_project(project_name)
                sys.exit(0)
            else:
                # Assume it's a project name to run
                project_name = sys.argv[1]
                projects = load_projects()
                
                if project_name not in projects:
                    print(f"Error: Project '{project_name}' does not exist.")
                    print("Use 'filedump svd' to see a list of available projects.")
                    sys.exit(1)
                
                # Load project config and set up arguments for main function
                project = projects[project_name]
                class Args:
                    pass
                args = Args()
                args.source = project["origin"]
                args.destination = project["dest"]
                args.filter = project.get("filter")
                args.preserve_structure = project.get("preserve_structure", True)
                
                print(f"Running project '{project_name}':")
                print(f"  Source: {args.source}")
                print(f"  Destination: {args.destination}")
                if args.filter:
                    print(f"  Filter: {args.filter}")
                print(f"  Preserve structure: {args.preserve_structure}")
                print("")
                
                return args
    
    # Normal argument parsing
    parser.add_argument("source", help="Source directory to extract files from")
    parser.add_argument("destination", nargs="?", default=os.getcwd(),
                        help="Destination directory (defaults to current directory)")
    parser.add_argument("--filter", help="Filter pattern for files (e.g., '*.java')")
    parser.add_argument("--flat", action="store_false", dest="preserve_structure",
                        help="Don't preserve directory structure, copy all files to the destination root")
    
    return parser.parse_args()


def list_files(directory, pattern=None):
    """List all files in directory and subdirectories, with optional filtering."""
    all_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Apply filter if provided
            if pattern:
                if not glob.fnmatch.fnmatch(file, pattern):
                    continue

            all_files.append(file_path)

    return all_files


def create_directory_structure(source_dir, dest_dir, file_path):
    """Create the same directory structure in destination as in source."""
    rel_path = os.path.relpath(file_path, source_dir)
    dest_file_path = os.path.join(dest_dir, rel_path)
    os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
    return dest_file_path


def copy_files(file_list, source_dir, dest_dir, preserve_structure=True):
    """Copy all files from source to destination."""
    copied_count = 0
    total_size = 0
    
    # Track files that have been copied to handle duplicates
    copied_filenames = {}
    
    for file_path in file_list:
        # Get the relative path and file name
        rel_path = os.path.relpath(file_path, source_dir)
        file_name = os.path.basename(file_path)
        
        if preserve_structure:
            # Create the same directory structure in destination
            dest_file_path = os.path.join(dest_dir, rel_path)
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
        else:
            # Flat structure - put all files directly in destination
            # Handle duplicates by adding a suffix
            if file_name in copied_filenames:
                # File with this name already exists, add a suffix
                name_parts = os.path.splitext(file_name)
                suffix = copied_filenames[file_name] + 1
                copied_filenames[file_name] = suffix
                new_name = f"{name_parts[0]} - {suffix}{name_parts[1]}"
                dest_file_path = os.path.join(dest_dir, new_name)
            else:
                # First occurrence of this filename
                copied_filenames[file_name] = 1
                dest_file_path = os.path.join(dest_dir, file_name)
        
        # Copy the file
        shutil.copy2(file_path, dest_file_path)
        file_size = os.path.getsize(file_path)
        total_size += file_size
        copied_count += 1
        
        # Print progress
        if preserve_structure:
            print(f"Copied: {rel_path} ({format_size(file_size)})")
        else:
            print(f"Copied: {os.path.basename(dest_file_path)} ({format_size(file_size)})")
    
    return copied_count, total_size


def format_size(size_in_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0 or unit == 'GB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0


def main():
    # Print the version and config file location
    print(f"FileDump v1.3 - Project file: {CONFIG_FILE}")
    print("-" * 50)
    
    args = parse_arguments()
    
    # Validate source directory
    if not os.path.isdir(args.source):
        print(f"Error: Source directory '{args.source}' does not exist or is not a directory.")
        sys.exit(1)
    
    # Convert to absolute paths
    source_dir = os.path.abspath(args.source)
    dest_dir = os.path.abspath(args.destination)
    
    # Create destination if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {dest_dir}")
    if args.filter:
        print(f"Filter pattern: {args.filter}")
    
    # Check if we're preserving directory structure
    preserve_structure = getattr(args, 'preserve_structure', True)
    print(f"Preserve directory structure: {preserve_structure}")
    
    # Get file list
    print("\nListing files...")
    files = list_files(source_dir, args.filter)
    
    if not files:
        print("No files found matching the criteria.")
        sys.exit(0)
    
    print(f"Found {len(files)} files to copy.")
    
    # Confirm with user if a lot of files
    if len(files) > 100:
        confirm = input(f"Warning: About to copy {len(files)} files. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    # Copy files
    print("\nCopying files...")
    copied, total_size = copy_files(files, source_dir, dest_dir, preserve_structure)
    
    # Summary
    print("\nSummary:")
    print(f"  - Files copied: {copied}")
    print(f"  - Total size: {format_size(total_size)}")
    print(f"  - Destination: {dest_dir}")
    
    print("\nDone!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)