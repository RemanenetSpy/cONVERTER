@echo off
REM File Converter - Quick Start Script for Windows

echo.
echo =====================================
echo   FILE CONVERTER PRO - Quick Start
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js 16+
    pause
    exit /b 1
)

echo ✅ Python version:
python --version

echo.
echo ✅ Node.js version:
node --version

echo.
echo =====================================
echo   Starting Backend (Flask)
echo =====================================
echo.

cd backend-python

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ✅ Backend starting on http://localhost:5000
echo Press CTRL+C to stop the backend
echo.

start python app.py

echo.
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak

echo.
echo =====================================
echo   Starting Frontend (React)
echo =====================================
echo.

cd ..\converter\frontend

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo ✅ Frontend starting on http://localhost:3000
echo Press CTRL+C to stop the frontend
echo.
echo Opening browser...

start http://localhost:3000

call npm start

pause
