@echo off
echo ========================================
echo 77-8DOC - Stop Server
echo ========================================
echo.

echo Searching for uvicorn processes...
for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH ^| findstr /I "uvicorn"') do (
    echo Found Python process with uvicorn: PID %%a
    taskkill /F /PID %%a
    goto :found
)

:found
echo.
echo [INFO] Stopped uvicorn processes
echo.
echo ========================================
pause
