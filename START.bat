@echo off
echo ========================================
echo    AirGuardian - Inicio Rapido
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    echo Por favor instala Python 3.9 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar si Node.js esta instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no esta instalado
    echo Por favor instala Node.js 18 o superior desde https://nodejs.org/
    pause
    exit /b 1
)

echo [1/6] Verificando entorno virtual de Python...
if not exist "backend\venv" (
    echo Creando entorno virtual...
    cd backend
    python -m venv venv
    cd ..
)

echo [2/6] Instalando dependencias de Python...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo [3/6] Instalando dependencias de Node.js...
cd frontend
if not exist "node_modules" (
    call npm install
)
cd ..

echo.
echo ========================================
echo   Configuracion completada!
echo ========================================
echo.
echo Iniciando servidores...
echo.
echo Backend estara en: http://localhost:8000
echo Frontend estara en: http://localhost:5173
echo.
echo Presiona Ctrl+C para detener los servidores
echo.

REM Iniciar backend en una nueva ventana
start "AirGuardian Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Esperar 3 segundos para que el backend inicie
timeout /t 3 /nobreak >nul

REM Iniciar frontend en una nueva ventana
start "AirGuardian Frontend" cmd /k "cd frontend && npm run dev"

REM Esperar 5 segundos y abrir el navegador
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================
echo   AirGuardian esta corriendo!
echo ========================================
echo.
echo Para detener, cierra las ventanas de Backend y Frontend
echo.
pause

