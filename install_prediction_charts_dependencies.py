"""
Script para instalar dependencias necesarias para los gráficos de predicciones
"""
import subprocess
import sys
import os

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        print(f"Instalando {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] {package} instalado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error instalando {package}: {e}")
        return False

def main():
    print("Instalando dependencias para gráficos de predicciones...")
    print("=" * 60)

    # Dependencias necesarias para los gráficos de predicciones
    packages = [
        "pandas",
        "numpy", 
        "plotly",
        "scikit-learn",
        "folium"
    ]

    print("\nInstalando dependencias...")
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"RESUMEN DE INSTALACION:")
    print(f"[OK] Paquetes instalados exitosamente: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("[SUCCESS] Todas las dependencias se instalaron correctamente!")
        print("\n[FUNCIONALIDADES DISPONIBLES]:")
        print("1. Gráficos de análisis de impacto (azul vs rojo)")
        print("2. Timeline de contaminantes con predicciones")
        print("3. Comparación de escenarios futuros")
        print("4. Visualización de PM2.5, PM10, NO2 y O3")
        print("5. Descarga de gráficos en HTML")
        print("\n[PRÓXIMOS PASOS]:")
        print("1. Reinicia el servidor backend: python main.py")
        print("2. Accede a AirGuardian y selecciona una estación")
        print("3. Activa la capa de predicciones")
        print("4. Haz clic en 'Análisis' y luego en 'Forecast'")
        print("5. Explora los gráficos de predicciones detalladas")
    else:
        print("[WARNING] Algunas dependencias no se pudieron instalar.")
        print("Revisa los errores anteriores e intenta instalar manualmente:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()
