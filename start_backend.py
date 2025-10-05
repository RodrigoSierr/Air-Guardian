"""
Script para iniciar el backend de AirGuardian con los gráficos de predicciones
"""
import subprocess
import sys
import time
import os

def start_backend():
    """Iniciar el backend de AirGuardian"""
    print("Iniciando backend de AirGuardian con gráficos de predicciones...")
    print("=" * 60)
    
    # Cambiar al directorio del backend
    backend_dir = "C:\\Users\\Usuario\\Documents\\Air-Guardian"
    os.chdir(backend_dir)
    
    print(f"Directorio: {os.getcwd()}")
    print("Iniciando servidor backend...")
    print("\n[INSTRUCCIONES]:")
    print("1. El backend se iniciará en http://localhost:8000")
    print("2. Abre otra terminal para el frontend: npm run dev")
    print("3. Accede a AirGuardian en http://localhost:5173")
    print("4. Selecciona una estación y ve a 'Análisis' -> 'Forecast'")
    print("5. Verás los 3 tipos de gráficos con colores corregidos:")
    print("   - Análisis de Impacto (azul vs rojo)")
    print("   - Timeline de Contaminantes")
    print("   - Comparación de Escenarios")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
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
