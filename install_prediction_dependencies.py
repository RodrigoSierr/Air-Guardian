"""
Script para instalar las dependencias necesarias para el sistema de predicciones
"""
import subprocess
import sys
import os

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[OK] {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error instalando {package}: {e}")
        return False

def main():
    print("Instalando dependencias para el sistema de predicciones...")
    print("=" * 60)
    
    # Dependencias necesarias para el backend
    backend_packages = [
        "pandas",
        "numpy",
        "scikit-learn",
        "plotly",
        "folium"
    ]
    
    # Dependencias para el frontend (si es necesario)
    frontend_packages = [
        "leaflet.heat"
    ]
    
    print("\nInstalando dependencias del backend...")
    backend_success = 0
    for package in backend_packages:
        if install_package(package):
            backend_success += 1
    
    print(f"\nResumen de instalacion:")
    print(f"[OK] Paquetes instalados correctamente: {backend_success}/{len(backend_packages)}")
    
    if backend_success == len(backend_packages):
        print("\nTodas las dependencias se instalaron correctamente!")
        print("\nProximos pasos:")
        print("1. Reinicia el backend de AirGuardian")
        print("2. Reinicia el frontend de AirGuardian")
        print("3. Las funcionalidades de predicciones estaran disponibles")
        print("\nPara reiniciar el backend:")
        print("   cd backend")
        print("   python main.py")
        print("\nPara reiniciar el frontend:")
        print("   cd frontend")
        print("   npm start")
    else:
        print("\nAlgunas dependencias no se pudieron instalar.")
        print("   Revisa los errores anteriores y instala manualmente:")
        for package in backend_packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()
