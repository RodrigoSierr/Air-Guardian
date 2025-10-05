"""
Script de prueba para verificar que los gráficos de predicciones funcionen correctamente
"""
import requests
import json
import sys

def test_prediction_charts_api():
    """Probar los endpoints de gráficos de predicciones"""
    base_url = "http://localhost:8000"
    
    print("[TEST] PROBANDO API DE GRAFICOS DE PREDICCIONES")
    print("=" * 50)
    
    # 1. Probar endpoint de estaciones disponibles
    print("\n1. Probando endpoint de estaciones disponibles...")
    try:
        response = requests.get(f"{base_url}/api/prediction-charts/available-stations")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Estaciones disponibles: {data.get('total_stations', 0)}")
            print(f"[OK] Total registros: {data.get('total_records', 0)}")
        else:
            print(f"[ERROR] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Error conectando: {e}")
        return False
    
    # 2. Probar generación de gráfico de impacto
    print("\n2. Probando gráfico de análisis de impacto...")
    try:
        payload = {
            "station_id": "station_1",
            "chart_type": "impact",
            "pollutants": ["PM2_5", "PM10", "NO2", "O3"]
        }
        response = requests.post(f"{base_url}/api/prediction-charts/generate", 
                                json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Grafico de impacto generado")
            print(f"[OK] Estacion: {data.get('data_summary', {}).get('station_name', 'N/A')}")
            print(f"[OK] Registros: {data.get('data_summary', {}).get('total_records', 0)}")
        else:
            print(f"[ERROR] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # 3. Probar generación de gráfico de timeline
    print("\n3. Probando gráfico de timeline...")
    try:
        payload = {
            "station_id": "station_1",
            "chart_type": "timeline",
            "pollutants": ["PM2_5", "PM10", "NO2", "O3"]
        }
        response = requests.post(f"{base_url}/api/prediction-charts/generate", 
                                json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Grafico de timeline generado")
            print(f"[OK] Estacion: {data.get('data_summary', {}).get('station_name', 'N/A')}")
        else:
            print(f"[ERROR] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # 4. Probar generación de gráfico de comparación
    print("\n4. Probando gráfico de comparación...")
    try:
        payload = {
            "station_id": "station_1",
            "chart_type": "comparison",
            "pollutants": ["PM2_5", "PM10", "NO2", "O3"]
        }
        response = requests.post(f"{base_url}/api/prediction-charts/generate", 
                                json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Grafico de comparacion generado")
            print(f"[OK] Estacion: {data.get('data_summary', {}).get('station_name', 'N/A')}")
        else:
            print(f"[ERROR] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # 5. Probar endpoint HTML directo
    print("\n5. Probando endpoint HTML directo...")
    try:
        response = requests.get(f"{base_url}/api/prediction-charts/station_1/impact")
        if response.status_code == 200:
            html_content = response.text
            if "plotly" in html_content.lower():
                print("[OK] HTML generado correctamente con Plotly")
            else:
                print("[WARNING] HTML generado pero sin Plotly")
        else:
            print(f"[ERROR] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] PRUEBA COMPLETADA")
    print("\n[INSTRUCCIONES PARA USAR EN AIRGUARDIAN]:")
    print("1. Asegúrate de que el backend esté corriendo: python main.py")
    print("2. Abre AirGuardian en el navegador")
    print("3. Selecciona una estación en el mapa")
    print("4. Activa la capa de 'Predicciones'")
    print("5. Haz clic en 'Analisis' -> 'Forecast'")
    print("6. Haz clic en 'Ver Gráficos de Predicciones'")
    print("7. Navega entre los 3 tipos de gráficos")
    print("\n[COLORES ESPERADOS]:")
    print("- Datos Actuales (Histórico): AZUL (#3498db)")
    print("- Predicciones (Futuro): ROJO (#e74c3c)")

if __name__ == "__main__":
    test_prediction_charts_api()
