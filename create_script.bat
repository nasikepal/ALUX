@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   OBSIDIAN PRODUCTION OS - CREATE NEW SCRIPT
echo ========================================================

set VENV_PY=%~dp0.venv\Scripts\python.exe
set CLI_SCRIPT=%~dp008_AUTOMATION\Scripts\cli.py

set /p TITLE="Enter Script Title: "
set /p PROJECT="Enter Project Name: "
set /p FORMAT="Enter Format [youtube/documentary/commercial]: "

if "!FORMAT!"=="" set FORMAT=youtube

"%VENV_PY%" "%CLI_SCRIPT%" new-script --title "!TITLE!" --project "!PROJECT!" --format "!FORMAT!"

echo.
echo ========================================================
echo   SCRIPT CREATED IN 02_SCRIPTS\Draft\
echo ========================================================
pause
