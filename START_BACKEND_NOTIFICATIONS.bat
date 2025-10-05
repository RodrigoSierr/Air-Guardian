@echo off
echo Iniciando AirGuardian Backend con Notificaciones...
echo.
cd backend
echo Directorio actual: %CD%
echo.
echo Iniciando servidor en http://localhost:8000
echo.
echo Para detener el servidor, presiona Ctrl+C
echo.
python main.py
pause
