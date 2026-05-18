@echo off
echo ========================================
echo    Focus Monitor — Starting...
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: venv not found. Run setup first.
    pause
    exit
)

call venv\Scripts\activate

echo Starting backend server...
echo Open browser: http://localhost:8000/app/index.html
echo Press Ctrl+C to stop.
echo.

start "" "http://localhost:8000/app/index.html"
uvicorn main:app --reload
pause