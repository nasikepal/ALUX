@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   OBSIDIAN PRODUCTION OS - PIPELINE LAUNCHER
echo ========================================================

set VENV_PY=%~dp0.venv\Scripts\python.exe
set CLI_SCRIPT=%~dp008_AUTOMATION\Scripts\cli.py

if "%~1"=="" (
    echo [!] No script path passed. Enter script path relative to vault root
    echo     or press ENTER to run on default: 02_SCRIPTS\Draft\The_Rise_of_AI.md
    set /p USER_INPUT="Script path: "
    if "!USER_INPUT!"=="" (
        set TARGET_SCRIPT=%~dp002_SCRIPTS\Draft\The_Rise_of_AI.md
    ) else (
        set TARGET_SCRIPT=%~dp0!USER_INPUT!
    )
) else (
    set TARGET_SCRIPT=%~1
)

echo.
echo [*] Target Script: !TARGET_SCRIPT!
echo [*] Executing Python Production Pipeline...
echo.

"%VENV_PY%" "%CLI_SCRIPT%" pipeline "!TARGET_SCRIPT!"

echo.
echo ========================================================
echo   PIPELINE EXECUTION COMPLETED
echo ========================================================
pause
