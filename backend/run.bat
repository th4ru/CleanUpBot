@echo off
REM Backend startup script for Windows

echo.
echo ===================================
echo System Manager Backend Startup
echo ===================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file with your settings!
    echo.
)

REM Run the application
echo.
echo Starting Flask backend...
echo Server will run on http://localhost:5000
echo.
python app.py

pause
