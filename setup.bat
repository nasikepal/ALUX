@echo off
echo ========================================================
echo   ALUX PRODUCTION OS - INITIAL SETUP
echo ========================================================

where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Found uv. Setting up virtual environment...
    uv venv "%~dp0.venv"
    call "%~dp0.venv\Scripts\activate.bat"
    uv pip install -r "%~dp0requirements.txt"
) else (
    echo [*] Setting up standard Python venv...
    python -m venv "%~dp0.venv"
    call "%~dp0.venv\Scripts\activate.bat"
    pip install -r "%~dp0requirements.txt"
)

echo.
echo ========================================================
echo   SETUP COMPLETED! RUN run_pipeline.bat TO START.
echo ========================================================
pause
