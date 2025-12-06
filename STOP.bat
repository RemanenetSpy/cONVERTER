@echo off
echo Stopping all servers...

REM Kill Python processes
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% == 0 (
    echo ✓ Backend stopped
) else (
    echo ✗ No backend running
)

REM Kill Node processes
taskkill /F /IM node.exe /T 2>nul
if %errorlevel% == 0 (
    echo ✓ Frontend stopped
) else (
    echo ✗ No frontend running
)

echo.
echo All servers stopped!
pause
