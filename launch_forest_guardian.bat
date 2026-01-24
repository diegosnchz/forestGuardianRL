@echo off
title ForestGuardian Command Center
echo --------------------------------------------------
echo 🌲 FOREST GUARDIAN - INITIALIZING COMMAND CENTER
echo --------------------------------------------------

:: Check for dependencies
python -c "import numba, xarray, torch, xgboost, panel" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Missing dependencies. Installing requirements_industrial.txt...
    pip install -r requirements_industrial.txt
)

echo 🚀 Launching HoloViz Panel Dashboard (2D MARL)...
echo 🔗 Access your Command Center at http://localhost:5007
echo.

python panel_rl_dashboard.py
pause
