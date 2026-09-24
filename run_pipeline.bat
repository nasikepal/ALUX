@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   OBSIDIAN PRODUCTION OS - PIPELINE LAUNCHER
echo ========================================================

set VENV_PY=%~dp0.venv\Scripts\python.exe
set CLI_SCRIPT=%~dp008_AUTOMATION\Scripts\cli.py

if "%~1"=="" (
    echo [*] Checking for available script drafts in 02_SCRIPTS\Draft...
    set FOUND_SCRIPT=
    for %%f in ("%~dp002_SCRIPTS\Draft\*.md") do (
        set FOUND_SCRIPT=%%~f
        echo     - %%~nxf
    )

    if "!FOUND_SCRIPT!"=="" (
        echo [!] No script draft found in 02_SCRIPTS\Draft.
        echo     Please enter path to your script markdown note:
        set /p USER_INPUT="Script path: "
        set TARGET_SCRIPT=%~dp0!USER_INPUT!
    ) else (
        echo.
        echo [?] Enter script filename in 02_SCRIPTS\Draft
        echo     or press ENTER to run on: !FOUND_SCRIPT!
        set /p USER_INPUT="Script (or ENTER): "
        if "!USER_INPUT!"=="" (
            set TARGET_SCRIPT=!FOUND_SCRIPT!
        ) else (
            set TARGET_SCRIPT=%~dp002_SCRIPTS\Draft\!USER_INPUT!
        )
    )
) else (
    set TARGET_SCRIPT=%~1
)

echo.
echo [*] Target Script: !TARGET_SCRIPT!
echo [*] Executing Production OS Pipeline...
echo.

"%VENV_PY%" "%CLI_SCRIPT%" pipeline "!TARGET_SCRIPT!"

echo.
echo ========================================================
echo   PIPELINE EXECUTION COMPLETED
echo ========================================================
pause
