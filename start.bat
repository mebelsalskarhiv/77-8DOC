@echo off
echo ========================================
echo 77-8DOC - Start Application
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python installed
echo.

REM Check virtual environment
echo [2/5] Checking virtual environment...
if not exist "venv\" (
    echo [WARNING] Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment found
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Check dependencies
echo [4/5] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Dependencies not installed
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies installed
)
echo.

REM Check .env file
echo [5/5] Checking configuration...
if not exist ".env" (
    echo [WARNING] .env file not found
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env >nul
        echo [WARNING] Edit .env file before starting!
        echo Open .env and set your 1C 7.7 database path
        notepad .env
        echo.
        echo After configuring .env, run this script again
        pause
        exit /b 0
    ) else (
        echo [ERROR] .env.example not found
        pause
        exit /b 1
    )
) else (
    echo [OK] .env file found
)
echo.

REM Check default settings in .env
findstr /C:"DB_PATH_77=D:\\Base77" .env >nul
if %errorlevel% equ 0 (
    echo [WARNING] Using default path in .env!
    echo Make sure the path to 1C 7.7 database is correct
    echo.
    choice /C YN /M "Open .env for editing"
    if %errorlevel% equ 1 (
        notepad .env
        echo.
        echo After configuring .env, run this script again
        pause
        exit /b 0
    )
)

REM Check 1C 7.7 COM server
echo.
echo ========================================
echo Checking 1C 7.7 COM server
echo ========================================
python -c "import win32com.client; win32com.client.Dispatch('V77.Application')" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 1C 7.7 COM server not registered!
    echo.
    echo To register, run as administrator:
    echo "C:\Program Files\1Cv77\BIN\1cv7s.exe" /REGSERVER
    echo.
    echo or
    echo "C:\Program Files (x86)\1Cv77\BIN\1cv7s.exe" /REGSERVER
    echo.
    choice /C YN /M "Continue without COM check"
    if %errorlevel% equ 2 (
        pause
        exit /b 0
    )
) else (
    echo [OK] 1C 7.7 COM server registered
)
echo.

REM Start application
echo ========================================
echo Starting server...
echo ========================================
echo.
echo Application will be available at:
echo http://localhost:8100
echo.
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8100 --reload

REM If server stopped
echo.
echo ========================================
echo Server stopped
echo ========================================
pause
