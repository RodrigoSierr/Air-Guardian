"""
Script para iniciar el backend de AirGuardian correctamente
"""
import subprocess
import sys
import os
import time

def start_backend():
    """Iniciar el backend desde el directorio correcto"""
    print("Iniciando backend de AirGuardian...")
    print("=" * 50)
    
    # Cambiar al directorio del backend
    backend_dir = "C:\\Users\\Usuario\\Documents\\Air-Guardian\\backend"
    os.chdir(backend_dir)
    
    print(f"Directorio: {os.getcwd()}")
    print("Iniciando servidor backend...")
    print("\n[ENDPOINTS DISPONIBLES]:")
    print("- http://localhost:8000/ (API principal)")
    print("- http://localhost:8000/api/prediction-charts/available-stations")
    print("- http://localhost:8000/api/prediction-charts/generate")
    print("- http://localhost:8000/api/prediction-layer/station_X")
    print("\n[INSTRUCCIONES]:")
    print("1. El backend se iniciará en http://localhost:8000")
    print("2. Abre otra terminal para el frontend: npm run dev")
    print("3. Accede a AirGuardian en http://localhost:5173")
    print("4. Los errores 404 deberían desaparecer")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    try:
        # Iniciar el servidor
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\nError iniciando el servidor: {e}")
        print("\nAsegúrate de que:")
        print("1. Estés en el directorio correcto")
        print("2. Las dependencias estén instaladas")
        print("3. No haya otro proceso usando el puerto 8000")

if __name__ == "__main__":
    start_backend()
