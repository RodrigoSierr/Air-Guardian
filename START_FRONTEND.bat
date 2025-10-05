@echo off
echo ========================================
echo    Iniciando Frontend de AirGuardian
echo ========================================
echo.

cd frontend

REM Verificar si existen node_modules
if not exist "node_modules" (
    echo [AVISO] node_modules no encontrado
    echo.
    echo Instalando dependencias...
    call npm install
    echo.
)

echo.
echo ========================================
echo   Iniciando Vite Dev Server
echo   URL: http://localhost:5173
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

npm run dev

pause

