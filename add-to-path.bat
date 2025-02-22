@echo off
setlocal enabledelayedexpansion

:: Add Current Directory to PATH
:: This script adds the current directory to your user PATH environment variable

echo ========================================
echo   Add Current Directory to PATH
echo ========================================

:: Get current directory (without trailing backslash)
set "CURRENT_DIR=%CD%"
echo Current directory: %CURRENT_DIR%

:: Check if running with admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Not running with administrator privileges.
    echo This script will only update the PATH for the current user.
    echo.
)

:: First check if the directory is already in PATH
set "IS_IN_PATH="
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"
echo %USER_PATH% | findstr /i /c:"%CURRENT_DIR%" >nul && set "IS_IN_PATH=1"

if defined IS_IN_PATH (
    echo.
    echo This directory is already in your PATH.
    echo.
    goto :END
)

:: Confirm with user
echo.
echo This will add the following directory to your PATH:
echo %CURRENT_DIR%
echo.
set /p CONFIRM="Are you sure you want to continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :END

:: Get the current PATH value for the user
set "NEW_PATH=%USER_PATH%"

:: If PATH is empty or doesn't exist, create it
if "%NEW_PATH%"=="" (
    set "NEW_PATH=%CURRENT_DIR%"
) else (
    :: Check if PATH ends with a semicolon, if not add one
    if not "%NEW_PATH:~-1%"==";" (
        set "NEW_PATH=%NEW_PATH%;"
    )
    set "NEW_PATH=%NEW_PATH%%CURRENT_DIR%"
)

:: Update the PATH for the current user
reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "%NEW_PATH%" /f

if %errorlevel% neq 0 (
    echo Failed to update PATH. Please try running as administrator.
    goto :END
)

echo.
echo Successfully added to PATH!
echo.

:: Notify other applications of the environment change
setx TEMP "%TEMP%" >nul 2>&1

echo NOTE: You'll need to restart any open command prompts or 
echo applications for the new PATH to take effect.
echo.