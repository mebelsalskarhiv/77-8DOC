@echo off
echo ========================================
echo 77-8DOC - Stop Server
echo ========================================
echo.

echo Searching for uvicorn processes...
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "uvicorn" >nul
if %errorlevel% equ 0 (
    echo Found Python processes with uvicorn
    echo.

    REM Show processes
    echo Active Python processes:
    for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH') do (
        echo PID: %%a
    )
    echo.

    choice /C YN /M "Stop all Python processes"
    if %errorlevel% equ 1 (
        echo Stopping processes...
        taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
        taskkill /F /IM python.exe /FI "COMMANDLINE eq *uvicorn*" >nul 2>&1
        echo [OK] Processes stopped
    ) else (
        echo Cancelled
    )
) else (
    echo [INFO] No active uvicorn processes found
)

echo.
echo ========================================
pause
