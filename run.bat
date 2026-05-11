@echo off
REM Quick start without checks - use only if environment is already configured

echo Starting 77-8DOC server...
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Run start.bat first to setup the environment
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8100 --reload

pause
