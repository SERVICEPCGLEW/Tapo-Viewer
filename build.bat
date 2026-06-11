@echo off
echo ===================================================
echo   Compilador - Tapo Viewer
echo ===================================================
echo.

echo Compilando Tapo Viewer con PyInstaller...
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.png;." main.py
echo.

echo ===================================================
echo   ¡Compilacion terminada! 
echo   El ejecutable esta en la carpeta "dist".
echo ===================================================
pause
