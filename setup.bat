@REM ======================================
@REM VOICE DOPPELGANGER - QUICK SETUP
@REM ======================================
@REM This script sets up the app on Windows

@echo off
echo.
echo ========================================
echo  AI VOICE DOPPELGANGER - SETUP WIZARD
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Please download Python from: https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python found!
python --version

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt

REM Setup instructions
echo.
echo [4/4] Setup instructions...
echo.
echo ========================================
echo  NEXT STEPS
echo ========================================
echo.
echo 1. Get your ElevenLabs API key:
echo    - Visit: https://elevenlabs.io/app/api
echo    - Sign up for free and get your API key
echo.
echo 2. Configure the API key:
echo    - Open the .env file in this directory
echo    - Replace 'your_api_key_here' with your actual API key
echo    - Save the file
echo.
echo 3. Start the server:
echo    - Run: python app.py
echo    - Open: http://localhost:5000 in your browser
echo.
echo ========================================
echo.
pause
