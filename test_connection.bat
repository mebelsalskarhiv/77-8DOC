@echo off
echo ========================================
echo 77-8DOC - Test 1C 7.7 Connection
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found
    echo Run start.bat first
    pause
    exit /b 1
)

REM Check .env
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Run start.bat first
    pause
    exit /b 1
)

echo Reading settings from .env...
echo.

REM Create temporary Python script for testing
echo import os > test_connection.py
echo from dotenv import load_dotenv >> test_connection.py
echo import sys >> test_connection.py
echo sys.path.insert(0, 'venv/Lib/site-packages') >> test_connection.py
echo import pythoncom >> test_connection.py
echo import win32com.client >> test_connection.py
echo. >> test_connection.py
echo load_dotenv() >> test_connection.py
echo. >> test_connection.py
echo db_path = os.getenv('DB_PATH_77', '') >> test_connection.py
echo db_user = os.getenv('DB_USER_77', '') >> test_connection.py
echo db_password = os.getenv('DB_PASSWORD_77', '') >> test_connection.py
echo. >> test_connection.py
echo print(f"Database: {db_path}") >> test_connection.py
echo print(f"User: {db_user}") >> test_connection.py
echo print(f"Password: {'*' * len(db_password) if db_password else '(empty)'}") >> test_connection.py
echo print() >> test_connection.py
echo. >> test_connection.py
echo print("Checking 1C 7.7 COM server...") >> test_connection.py
echo progids = ["V77.Application", "V77S.Application", "V77M.Application", "V77L.Application"] >> test_connection.py
echo found = None >> test_connection.py
echo for progid in progids: >> test_connection.py
echo     try: >> test_connection.py
echo         app = win32com.client.Dispatch(progid) >> test_connection.py
echo         found = progid >> test_connection.py
echo         print(f"[OK] Found COM server: {progid}") >> test_connection.py
echo         break >> test_connection.py
echo     except: >> test_connection.py
echo         pass >> test_connection.py
echo. >> test_connection.py
echo if not found: >> test_connection.py
echo     print("[ERROR] 1C 7.7 COM server not found!") >> test_connection.py
echo     print() >> test_connection.py
echo     print("Register COM server with command:") >> test_connection.py
echo     print('"C:\\Program Files\\1Cv77\\BIN\\1cv7s.exe" /REGSERVER') >> test_connection.py
echo     exit(1) >> test_connection.py
echo. >> test_connection.py
echo print() >> test_connection.py
echo print("Attempting to connect to 1C 7.7 database...") >> test_connection.py
echo. >> test_connection.py
echo try: >> test_connection.py
echo     pythoncom.CoInitialize() >> test_connection.py
echo     app = win32com.client.Dispatch(found) >> test_connection.py
echo     params = f'/D"{db_path}"' >> test_connection.py
echo     if db_user: >> test_connection.py
echo         params += f' /N"{db_user}"' >> test_connection.py
echo     if db_password: >> test_connection.py
echo         params += f' /P"{db_password}"' >> test_connection.py
echo     print(f"Parameters: {params.replace(db_password, '***') if db_password else params}") >> test_connection.py
echo     print() >> test_connection.py
echo     ok = app.Initialize(app.RMTrade, params, "NO_SPLASH_SHOW") >> test_connection.py
echo     if ok: >> test_connection.py
echo         print("[OK] Connection successful!") >> test_connection.py
echo         print() >> test_connection.py
echo         print("Checking data access...") >> test_connection.py
echo         try: >> test_connection.py
echo             query = app.CreateObject("Запрос") >> test_connection.py
echo             print("[OK] Query object created successfully") >> test_connection.py
echo             print() >> test_connection.py
echo             print("All checks passed! Application is ready.") >> test_connection.py
echo         except Exception as e: >> test_connection.py
echo             print(f"[WARNING] Error creating Query object: {e}") >> test_connection.py
echo     else: >> test_connection.py
echo         print("[ERROR] 1C returned error in Initialize()") >> test_connection.py
echo         print() >> test_connection.py
echo         print("Possible reasons:") >> test_connection.py
echo         print("1. Invalid database path") >> test_connection.py
echo         print("2. Invalid login or password") >> test_connection.py
echo         print("3. No access to network folder") >> test_connection.py
echo         print("4. Database is locked or corrupted") >> test_connection.py
echo         exit(1) >> test_connection.py
echo     pythoncom.CoUninitialize() >> test_connection.py
echo except Exception as e: >> test_connection.py
echo     print(f"[ERROR] {e}") >> test_connection.py
echo     pythoncom.CoUninitialize() >> test_connection.py
echo     exit(1) >> test_connection.py

echo Running test...
echo.
call venv\Scripts\python.exe test_connection.py
set TEST_RESULT=%errorlevel%

REM Delete temporary file
del test_connection.py >nul 2>&1

echo.
if %TEST_RESULT% equ 0 (
    echo [SUCCESS] All tests passed!
) else (
    echo [FAILED] Tests failed. Check the errors above.
)
echo ========================================
pause
exit /b %TEST_RESULT%
