@echo off
echo ========================================
echo    Iniciando Backend de AirGuardian
echo ========================================
echo.

cd backend

REM Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado
    echo.
    echo Creando entorno virtual...
    python -m venv venv
    echo.
    echo Instalando dependencias...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

echo.
echo ========================================
echo   Iniciando servidor FastAPI
echo   URL: http://localhost:8000
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python main.py

pause

