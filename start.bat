@echo off
cd /d "%~dp0"
title Servidor DSU - Giroscopio ASUS ROG Ally
cls

echo =======================================================
echo    Iniciando Servidor DSU para Giroscopio (Citra)
echo =======================================================
echo.

:: Verifica que Python esté disponible
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Error: Python no esta instalado o no esta en el PATH.
    echo     Instalalo desde https://www.python.org/downloads/ marcando "Add to PATH".
    echo.
    pause
    exit /b 1
)

:: Verifica si winsdk se puede importar con el mismo Python del script
python -c "import winsdk" >nul 2>&1
if %errorlevel% neq 0 (
    echo [+] La libreria 'winsdk' no esta instalada. Instalando ahora...
    python -m pip install winsdk
    if %errorlevel% neq 0 (
        echo [-] Error al instalar winsdk. Asegurate de tener internet y de correr este .bat como administrador si hace falta.
        echo.
        pause
        exit /b 1
    )
    echo [+] Instalacion exitosa.
    echo.
)

:: Verifica que el script de Python exista en la misma carpeta
if not exist "dsu_server.py" (
    echo [-] Error: No se encontro el archivo 'dsu_server.py' en esta carpeta.
    echo Asegurate de poner este archivo .bat JUNTO al script de Python.
    echo.
    pause
    exit /b 1
)

echo [+] Levantando el servidor UDP...
echo [i] Mantene esta ventana abierta mientras juegues en Citra.
echo.
python dsu_server.py

echo.
echo [-] El servidor se cerro. Revisa el mensaje de error si aparecio uno.
pause