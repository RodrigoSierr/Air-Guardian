"""
Script para verificar si el backend está funcionando
"""
import requests
import time

def check_backend():
    """Verificar si el backend está funcionando"""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("[SUCCESS] Backend funcionando correctamente")
            print(f"Respuesta: {response.json()}")
            return True
        else:
            print(f"[ERROR] Backend respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al backend en http://localhost:8000")
        print("El backend no está corriendo")
        return False
    except Exception as e:
        print(f"[ERROR] Error verificando backend: {e}")
        return False

def check_prediction_endpoints():
    """Verificar endpoints de predicciones"""
    endpoints = [
        '/api/prediction-charts/available-stations',
        '/api/prediction-layer/station_1'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            print(f"[OK] {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {endpoint}: {e}")

if __name__ == "__main__":
    print("Verificando backend de AirGuardian...")
    print("=" * 40)
    
    if check_backend():
        print("\nVerificando endpoints de predicciones...")
        check_prediction_endpoints()
    else:
        print("\n[INSTRUCCIONES]:")
        print("1. Abre una nueva terminal")
        print("2. cd 'C:\\Users\\Usuario\\Documents\\Air-Guardian'")
        print("3. python main.py")
        print("4. Espera a que aparezca 'Uvicorn running on http://0.0.0.0:8000'")
        print("5. Luego ejecuta este script nuevamente")
