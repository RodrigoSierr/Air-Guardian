@echo off
echo Probando sistema de notificaciones...
echo.

echo 1. Verificando que el backend este funcionando...
curl -s http://localhost:8000 > nul
if %errorlevel% neq 0 (
    echo ERROR: El backend no esta funcionando en http://localhost:8000
    echo Por favor, ejecuta START_BACKEND_NOTIFICATIONS.bat primero
    pause
    exit /b 1
)
echo ✓ Backend funcionando correctamente

echo.
echo 2. Probando endpoint de notificaciones...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:8000/api/send-notification' -Method POST -ContentType 'application/json' -Body '{\"name\":\"Test\",\"email\":\"test@example.com\",\"phone\":\"+123\",\"city\":\"Lima\",\"location\":{\"lat\":-12,\"lon\":-77}}' } catch { Write-Host 'Error: ' $_.Exception.Message }"

echo.
echo 3. Verificando frontend...
echo Abre http://localhost:5173 en tu navegador
echo Haz clic en el boton "Notificaciones" en la parte superior
echo.

echo ✓ Sistema de notificaciones listo para usar
pause
