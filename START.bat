@echo off
echo ========================================
echo   File Converter - Startup Script
echo ========================================
echo.

REM Start Backend
echo [1/2] Starting Backend Server...
cd backend-python
start cmd /k "python app.py"
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend
echo [2/2] Starting Frontend Server...
cd converter\frontend
start cmd /k "npm start"
cd ..\..

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window...
pause > nul
