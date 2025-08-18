@echo off
echo.
echo =========================================
echo  Starmap - Felgenland Saga v0.0.1
echo  3D Interactive Stellar Cartography
echo =========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

:: Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please install pip or use python -m ensurepip
    pause
    exit /b 1
)

:: Install requirements if needed
echo Checking dependencies...
pip install -r requirements.txt --quiet

:: Start the application
echo.
echo Starting Starmap application...
echo.
echo ========================================
echo  Access the starmap at:
echo  http://localhost:8080
echo.
echo  Login credentials:
echo  Username: admin
echo  Password: felgenland_secure_2025
echo ========================================
echo.

python app.py

:: Keep window open on error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)