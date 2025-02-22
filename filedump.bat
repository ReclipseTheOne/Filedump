@echo off
:: FileDump Batch File Wrapper
:: This allows you to run filedump from anywhere

:: Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

:: Check if Python is installed and in PATH
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Run the filedump.py script with all arguments passed to this batch file
python "%SCRIPT_DIR%filedump.py" %*

:: If no arguments were provided, show help
if "%~1"=="" (
    echo.
    echo FileDump - File Directory Extraction Utility
    echo.
    echo Usage:
    echo   filedump source_directory [destination_directory] [--filter PATTERN] [--flat]
    echo   filedump svd                  - List all saved projects
    echo   filedump svd NAME             - Run a saved project
    echo   filedump svd create           - Create a project step by step
    echo   filedump svd save NAME SRC DST - Save a project
    echo   filedump svd edit NAME        - Edit a saved project
    echo   filedump svd delete NAME      - Delete a saved project
    echo.
)

:: Pause only if double-clicked (not if run from command line)
echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause