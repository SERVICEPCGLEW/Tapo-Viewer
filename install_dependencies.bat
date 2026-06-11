@echo off
echo ===================================================
echo   Instalador de Dependencias - Tapo Viewer
echo ===================================================
echo.

echo 1. Comprobando e instalando VLC Media Player via winget...
winget install --id VideoLAN.VLC -e --accept-package-agreements --accept-source-agreements
echo.

echo 2. Instalando dependencias de Python (PyQt6, python-vlc, pyinstaller)...
pip install -r requirements.txt
echo.

echo ===================================================
echo   ¡Instalacion completada!
echo ===================================================
pause
