@echo off
cd /d "%~dp0"
python -c "import winsdk" 2>nul
if errorlevel 1 (
    echo Instalando winsdk...
    python -m pip install winsdk
)
python diagnostico_sensores.py
pause