@echo off
echo ========================================================
echo   OBSIDIAN PRODUCTION OS - LOCAL MEDIA INDEXER
echo ========================================================

set VENV_PY=%~dp0.venv\Scripts\python.exe
set CLI_SCRIPT=%~dp008_AUTOMATION\Scripts\cli.py

"%VENV_PY%" "%CLI_SCRIPT%" index-local

echo.
echo ========================================================
echo   MEDIA INDEXING COMPLETED
echo ========================================================
pause
