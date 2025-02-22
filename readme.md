## FileDump - An utility to extract all the files from a specified directory

Currently the project also comes with a .bat wrapper for CLI usage! Run <b>add-to-path.bat</b> as administrator to add the current directory to PATH and use <b>filedump</b> anywhere directly in CLI!

### Usage:
    python filedump.py source_directory [destination_directory] [--filter PATTERN]
    python filedump.py svd                  # List all saved projects
    python filedump.py svd NAME             # Run a saved project
    python filedump.py svd save NAME        # Save current args as a project
    python filedump.py svd create           # Create a project step by step
    python filedump.py svd edit NAME        # Edit a saved project
    python filedump.py svd delete NAME      # Delete a saved project

### Arguments:
    source_directory     - The directory to extract files from (required)
    destination_directory - Where to save the extracted files (optional, defaults to current directory)
    --filter PATTERN     - Only include files matching this pattern (optional, supports glob patterns)
    --flat               - Don't preserve directory structure, copy all files to the destination root