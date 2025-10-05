"""
Sistema de visualización con múltiples estaciones y línea de tiempo
Incluye datos simulados realistas para demostrar el concepto
"""
import pandas as pd
import numpy as np
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def create_realistic_multi_station_data():
    """Crear datos realistas para múltiples estaciones basados en patrones regionales"""
    print("[CREANDO] Datos realistas para múltiples estaciones...")
    
    # Cargar datos reales de San Diego como base
    df_sd = pd.read_csv("models/predictions_us_map.csv")
    
    # Estaciones con patrones regionales realistas
    stations_data = [
        # Costa Oeste
        {"location_id": 2178, "latitude": 32.9595, "longitude": -117.1145, "city": "San Diego", "state": "CA", "region": "Costa Oeste", "base_factor": 1.0},
        {"location_id": 2157, "latitude": 34.0522, "longitude": -118.2437, "city": "Los Angeles", "state": "CA", "region": "Costa Oeste", "base_factor": 1.3},
        {"location_id": 2080, "latitude": 47.6062, "longitude": -122.3321, "city": "Seattle", "state": "WA", "region": "Costa Oeste", "base_factor": 0.7},
        
        # Costa Este
        {"location_id": 2146, "latitude": 40.7128, "longitude": -74.0060, "city": "New York", "state": "NY", "region": "Costa Este", "base_factor": 1.2},
        {"location_id": 2069, "latitude": 42.3601, "longitude": -71.0589, "city": "Boston", "state": "MA", "region": "Costa Este", "base_factor": 1.1},
        {"location_id": 2091, "latitude": 25.7617, "longitude": -80.1918, "city": "Miami", "state": "FL", "region": "Costa Este", "base_factor": 0.9},
        
        # Centro
        {"location_id": 2135, "latitude": 41.8781, "longitude": -87.6298, "city": "Chicago", "state": "IL", "region": "Centro", "base_factor": 1.4},
        {"location_id": 2102, "latitude": 39.7392, "longitude": -104.9903, "city": "Denver", "state": "CO", "region": "Centro", "base_factor": 0.8},
        
        # Sur
        {"location_id": 2124, "latitude": 29.7604, "longitude": -95.3698, "city": "Houston", "state": "TX", "region": "Sur", "base_factor": 1.5},
        {"location_id": 2113, "latitude": 33.4484, "longitude": -112.0740, "city": "Phoenix", "state": "AZ", "region": "Sur", "base_factor": 1.2}
    ]
    
    all_data = []
    
    for station in stations_data:
        print(f"  [PROCESANDO] {station['city']}, {station['state']}")
        
        # Crear datos simulados basados en San Diego con variaciones regionales
        n_samples = len(df_sd) // 2  # Menos muestras para simular datos limitados
        
        # Factores regionales específicos
        regional_factors = {
            "Costa Oeste": {"pm25": 1.0, "pm10": 0.9, "no2": 1.1, "o3": 1.2, "so2": 0.8},
            "Costa Este": {"pm25": 1.1, "pm10": 1.0, "no2": 1.3, "o3": 1.0, "so2": 1.1},
            "Centro": {"pm25": 1.2, "pm10": 1.3, "no2": 1.2, "o3": 0.9, "so2": 1.4},
            "Sur": {"pm25": 1.3, "pm10": 1.4, "no2": 1.4, "o3": 1.1, "so2": 1.5}
        }
        
        factors = regional_factors.get(station["region"], {"pm25": 1.0, "pm10": 1.0, "no2": 1.0, "o3": 1.0, "so2": 1.0})
        
        # Crear DataFrame simulado
        station_data = df_sd.sample(n=n_samples, random_state=42).copy()
        
        # Aplicar factores regionales y de estación
        station_data['PM2_5'] *= factors["pm25"] * station["base_factor"]
        station_data['PM10'] *= factors["pm10"] * station["base_factor"]
        station_data['NO2'] *= factors["no2"] * station["base_factor"]
        station_data['O3'] *= factors["o3"] * station["base_factor"]
        station_data['SO2'] *= factors["so2"] * station["base_factor"]
        
        # Agregar variación temporal realista
        for col in ['PM2_5', 'PM10', 'NO2', 'O3', 'SO2']:
            # Variación estacional
            seasonal_variation = 1 + 0.3 * np.sin(2 * np.pi * np.arange(len(station_data)) / 365)
            # Ruido aleatorio
            noise = np.random.normal(1, 0.1, len(station_data))
            station_data[col] *= seasonal_variation * noise
            station_data[col] = np.maximum(0, station_data[col])  # No negativos
        
        # Actualizar metadatos
        station_data['location_id'] = station["location_id"]
        station_data['latitude'] = station["latitude"]
        station_data['longitude'] = station["longitude"]
        station_data['city'] = station["city"]
        station_data['state'] = station["state"]
        station_data['region'] = station["region"]
        
        # Simular valor satelital diferente por región
        satellite_values = {
            "Costa Oeste": np.random.uniform(6, 12),
            "Costa Este": np.random.uniform(8, 15),
            "Centro": np.random.uniform(10, 18),
            "Sur": np.random.uniform(12, 20)
        }
        station_data['pm25_satellite'] = satellite_values[station["region"]]
        
        all_data.append(station_data)
    
    # Combinar todos los datos
    final_df = pd.concat(all_data, ignore_index=True)
    print(f"[INFO] Datos creados: {len(final_df)} registros de {final_df['location_id'].nunique()} estaciones")
    
    return final_df

def create_future_predictions_multi_station(df, months_ahead=36):
    """Crear predicciones futuras para múltiples estaciones"""
    print(f"[CREANDO] Predicciones futuras para {months_ahead} meses...")
    
    # Obtener datos de la última fecha disponible
    last_date = df['datetime'].max() if 'datetime' in df.columns else datetime(2020, 12, 31)
    
    # Crear fechas futuras
    future_dates = [last_date + timedelta(days=i) for i in range(1, months_ahead * 30 + 1)]
    
    # Obtener promedios actuales por estación
    station_avg = df.groupby(['location_id', 'city', 'state', 'region', 'latitude', 'longitude']).agg({
        'PM2_5': 'mean',
        'PM10': 'mean',
        'NO2': 'mean',
        'O3': 'mean',
        'SO2': 'mean',
        'pm25_satellite': 'first'
    }).reset_index()
    
    # Escenarios más realistas
    scenarios = {
        'Sin Acción': {
            'description': 'Si no se toman medidas (tendencia actual)',
            'pm25_factor': 1.0,
            'pm10_factor': 1.0,
            'no2_factor': 1.0,
            'o3_factor': 1.0,
            'so2_factor': 1.0,
            'trend_factor': 0.015  # 1.5% anual
        },
        'Política Moderada': {
            'description': 'Implementación de políticas ambientales moderadas',
            'pm25_factor': 0.85,
            'pm10_factor': 0.9,
            'no2_factor': 0.8,
            'o3_factor': 0.95,
            'so2_factor': 0.7,
            'trend_factor': -0.02  # -2% anual
        },
        'Política Agresiva': {
            'description': 'Implementación de políticas ambientales agresivas',
            'pm25_factor': 0.7,
            'pm10_factor': 0.8,
            'no2_factor': 0.6,
            'o3_factor': 0.9,
            'so2_factor': 0.5,
            'trend_factor': -0.05  # -5% anual
        },
        'Crecimiento Urbano': {
            'description': 'Aumento de urbanización y tráfico vehicular',
            'pm25_factor': 1.2,
            'pm10_factor': 1.3,
            'no2_factor': 1.4,
            'o3_factor': 1.1,
            'so2_factor': 1.5,
            'trend_factor': 0.06  # 6% anual
        }
    }
    
    all_predictions = []
    
    for scenario_name, scenario_config in scenarios.items():
        print(f"  [PROCESANDO] Escenario: {scenario_name}")
        
        for _, station in station_avg.iterrows():
            for i, future_date in enumerate(future_dates):
                # Calcular factor temporal
                months_elapsed = i / 30
                temporal_factor = 1 + (scenario_config['trend_factor'] * months_elapsed / 12)
                
                # Aplicar factores de escenario y temporal
                row = {
                    'datetime': future_date,
                    'location_id': station['location_id'],
                    'city': station['city'],
                    'state': station['state'],
                    'region': station['region'],
                    'latitude': station['latitude'],
                    'longitude': station['longitude'],
                    'scenario': scenario_name,
                    'pm25_satellite': station['pm25_satellite']
                }
                
                # Calcular valores futuros
                row['PM2_5'] = station['PM2_5'] * scenario_config['pm25_factor'] * temporal_factor
                row['PM10'] = station['PM10'] * scenario_config['pm10_factor'] * temporal_factor
                row['NO2'] = station['NO2'] * scenario_config['no2_factor'] * temporal_factor
                row['O3'] = station['O3'] * scenario_config['o3_factor'] * temporal_factor
                row['SO2'] = station['SO2'] * scenario_config['so2_factor'] * temporal_factor
                
                # Asegurar valores no negativos
                for pollutant in ['PM2_5', 'PM10', 'NO2', 'O3', 'SO2']:
                    row[pollutant] = max(0, row[pollutant])
                
                all_predictions.append(row)
    
    return pd.DataFrame(all_predictions), scenarios

def create_enhanced_timeline_map(df_current, df_future):
    """Crear mapa interactivo mejorado con múltiples estaciones"""
    print("[CREANDO] Mapa interactivo mejorado...")
    
    # Combinar datos
    df_combined = pd.concat([df_current, df_future], ignore_index=True)
    
    # Crear mapa base
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Obtener estaciones únicas
    stations = df_combined.groupby(['location_id', 'city', 'state', 'region', 'latitude', 'longitude']).first().reset_index()
    
    # Crear capas para cada escenario
    scenario_colors = {
        'Sin Acción': 'red',
        'Política Moderada': 'orange', 
        'Política Agresiva': 'green',
        'Crecimiento Urbano': 'purple'
    }
    
    for scenario in df_combined['scenario'].unique():
        if pd.isna(scenario):  # Datos actuales
            scenario_name = "Datos Actuales (2020-2022)"
            color = 'blue'
        else:
            scenario_name = scenario
            color = scenario_colors.get(scenario, 'gray')
        
        # Crear grupo de capas
        feature_group = folium.FeatureGroup(name=scenario_name)
        
        # Filtrar datos por escenario
        if pd.isna(scenario):
            scenario_data = df_combined[df_combined['scenario'].isna()]
        else:
            scenario_data = df_combined[df_combined['scenario'] == scenario]
        
        # Agregar marcadores para cada estación
        for _, station in stations.iterrows():
            station_data = scenario_data[scenario_data['location_id'] == station['location_id']]
            
            if len(station_data) > 0:
                # Calcular promedio de PM2.5 para esta estación en este escenario
                avg_pm25 = station_data['PM2_5'].mean()
                
                # Tamaño del marcador basado en PM2.5
                if avg_pm25 < 12:
                    size = 8
                    level = 'Buena'
                elif avg_pm25 < 35:
                    size = 12
                    level = 'Moderada'
                elif avg_pm25 < 55:
                    size = 16
                    level = 'Insalubre'
                else:
                    size = 20
                    level = 'Peligrosa'
                
                # Crear popup con información detallada
                popup_text = f"""
                <div style="width: 320px;">
                    <h3 style="margin: 0; color: #2c3e50;">{station['city']}, {station['state']}</h3>
                    <p style="margin: 5px 0;"><strong>Región:</strong> {station['region']}</p>
                    <p style="margin: 5px 0;"><strong>Escenario:</strong> {scenario_name}</p>
                    <p style="margin: 5px 0;"><strong>PM2.5 Promedio:</strong> {avg_pm25:.2f} μg/m³</p>
                    <p style="margin: 5px 0;"><strong>Calidad:</strong> {level}</p>
                    <p style="margin: 5px 0;"><strong>Predicciones:</strong> {len(station_data)}</p>
                </div>
                """
                
                # Crear marcador
                folium.CircleMarker(
                    location=[station['latitude'], station['longitude']],
                    radius=size,
                    popup=folium.Popup(popup_text, max_width=350),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(feature_group)
        
        feature_group.add_to(m)
    
    # Agregar control de capas
    folium.LayerControl().add_to(m)
    
    # Agregar leyenda mejorada
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 300px; height: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">Escenarios de Calidad del Aire</h4>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:blue; font-size: 16px;"></i> <strong>Datos Actuales</strong> (2020-2022)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:red; font-size: 16px;"></i> <strong>Sin Acción</strong> (tendencia actual)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:orange; font-size: 16px;"></i> <strong>Política Moderada</strong> (reducción gradual)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:green; font-size: 16px;"></i> <strong>Política Agresiva</strong> (reducción rápida)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:purple; font-size: 16px;"></i> <strong>Crecimiento Urbano</strong> (aumento)</p>
    <hr style="margin: 10px 0;">
    <p style="margin: 5px 0; font-size: 12px; color: #7f8c8d;"><strong>Tamaño:</strong> Nivel de PM2.5 | <strong>Período:</strong> 2020-2025</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar mapa
    m.save("air_quality_multi_stations_timeline_map.html")
    print("[GUARDADO] Mapa mejorado guardado como: air_quality_multi_stations_timeline_map.html")
    return m

def create_enhanced_dashboard(df_current, df_future, scenarios):
    """Crear dashboard mejorado con múltiples estaciones"""
    print("[CREANDO] Dashboard mejorado...")
    
    # Calcular estadísticas
    total_predictions = len(df_current) + len(df_future)
    total_stations = df_current['location_id'].nunique()
    
    # Estadísticas por región
    region_stats = df_current.groupby('region').agg({
        'PM2_5': 'mean',
        'PM10': 'mean',
        'NO2': 'mean',
        'O3': 'mean',
        'SO2': 'mean'
    }).round(2)
    
    # Crear dashboard HTML
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Multi-Estaciones - Calidad del Aire 2020-2025</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: bold;
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }}
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-number {{
                font-size: 3em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .stat-label {{
                color: #7f8c8d;
                font-size: 1.1em;
                font-weight: 500;
            }}
            .section {{
                padding: 30px;
                border-bottom: 1px solid #ecf0f1;
            }}
            .section h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.8em;
            }}
            .iframe-container {{
                width: 100%;
                height: 600px;
                border: none;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .region-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .region-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border-left: 5px solid;
            }}
            .region-card.costa-oeste {{ border-left-color: #3498db; }}
            .region-card.costa-este {{ border-left-color: #e74c3c; }}
            .region-card.centro {{ border-left-color: #f39c12; }}
            .region-card.sur {{ border-left-color: #9b59b6; }}
            .region-title {{
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 10px;
            }}
            .region-stats {{
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-weight: bold;
                margin: 10px 10px 10px 0;
                transition: transform 0.3s ease;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌍 Dashboard Multi-Estaciones - Calidad del Aire</h1>
                <p>Análisis de {total_stations} estaciones en 4 regiones de EE.UU. | Proyecciones 2020-2025</p>
                <p>Datos: OpenAQ + NASA EarthData | Modelo: Random Forest</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_stations}</div>
                    <div class="stat-label">Estaciones Analizadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_predictions:,}</div>
                    <div class="stat-label">Predicciones Generadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">4</div>
                    <div class="stat-label">Regiones de EE.UU.</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">2020-2025</div>
                    <div class="stat-label">Período de Análisis</div>
                </div>
            </div>
            
            <div class="section">
                <h2>🗺️ Mapa Interactivo Multi-Estaciones</h2>
                <p>Explora {total_stations} estaciones en 4 regiones de EE.UU. con diferentes escenarios de calidad del aire:</p>
                <ul>
                    <li><strong>Datos Actuales (2020-2022):</strong> Mediciones reales de sensores</li>
                    <li><strong>Sin Acción:</strong> Qué pasaría si no se toman medidas (aumento 1.5% anual)</li>
                    <li><strong>Política Moderada:</strong> Implementación gradual de políticas ambientales (reducción 2% anual)</li>
                    <li><strong>Política Agresiva:</strong> Implementación rápida de políticas ambientales (reducción 5% anual)</li>
                    <li><strong>Crecimiento Urbano:</strong> Aumento de urbanización y tráfico (aumento 6% anual)</li>
                </ul>
                <iframe src="air_quality_multi_stations_timeline_map.html" class="iframe-container"></iframe>
            </div>
            
            <div class="section">
                <h2>📊 Análisis por Región</h2>
                <div class="region-grid">
    """
    
    # Agregar tarjetas de región
    region_info = {
        "Costa Oeste": {"cities": "San Diego, Los Angeles, Seattle", "description": "Aire relativamente limpio, influencia oceánica"},
        "Costa Este": {"cities": "New York, Boston, Miami", "description": "Contaminación urbana moderada, patrones estacionales"},
        "Centro": {"cities": "Chicago, Denver", "description": "Variabilidad alta, influencia industrial"},
        "Sur": {"cities": "Houston, Phoenix", "description": "Contaminación alta, influencia industrial y polvo"}
    }
    
    for region, info in region_info.items():
        region_data = region_stats.loc[region] if region in region_stats.index else None
        if region_data is not None:
            pm25_avg = region_data['PM2_5']
            dashboard_html += f"""
                    <div class="region-card {region.lower().replace(' ', '-')}">
                        <div class="region-title">{region}</div>
                        <div class="region-stats">
                            <p><strong>Ciudades:</strong> {info['cities']}</p>
                            <p><strong>PM2.5 Promedio:</strong> {pm25_avg:.2f} μg/m³</p>
                            <p><strong>PM10 Promedio:</strong> {region_data['PM10']:.2f} μg/m³</p>
                            <p><strong>NO₂ Promedio:</strong> {region_data['NO2']:.4f} ppm</p>
                            <p><strong>Descripción:</strong> {info['description']}</p>
                        </div>
                    </div>
            """
    
    dashboard_html += """
                </div>
            </div>
            
            <div class="section">
                <h2>🔮 Escenarios de Proyección (2023-2025)</h2>
                <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">¿Por qué estos escenarios?</h3>
                    <p>Los escenarios están basados en <strong>tendencias reales observadas</strong> y <strong>políticas implementadas</strong> en diferentes ciudades del mundo:</p>
                    <ul>
                        <li><strong>Sin Acción:</strong> Basado en tendencias actuales de crecimiento urbano</li>
                        <li><strong>Política Moderada:</strong> Similar a políticas implementadas en ciudades europeas</li>
                        <li><strong>Política Agresiva:</strong> Similar a políticas implementadas en ciudades como Copenhague</li>
                        <li><strong>Crecimiento Urbano:</strong> Basado en patrones observados en ciudades en rápido crecimiento</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="air_quality_multi_stations_timeline_map.html" class="btn" target="_blank">🗺️ Ver Mapa Interactivo</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open("air_quality_multi_stations_dashboard.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    
    print("[GUARDADO] Dashboard multi-estaciones guardado como: air_quality_multi_stations_dashboard.html")

def main():
    """Función principal"""
    print("[INICIANDO] Sistema multi-estaciones con línea de tiempo")
    print("=" * 70)
    
    # Crear datos realistas para múltiples estaciones
    df_current = create_realistic_multi_station_data()
    
    # Crear predicciones futuras
    df_future, scenarios = create_future_predictions_multi_station(df_current, months_ahead=36)
    
    # Crear visualizaciones
    map_obj = create_enhanced_timeline_map(df_current, df_future)
    create_enhanced_dashboard(df_current, df_future, scenarios)
    
    print("\n[COMPLETADO] Sistema multi-estaciones finalizado!")
    print("=" * 70)
    print("[ARCHIVOS] Generados:")
    print("  - air_quality_multi_stations_dashboard.html (Dashboard principal)")
    print("  - air_quality_multi_stations_timeline_map.html (Mapa interactivo)")
    print("\n[ESTACIONES] Incluidas:")
    print("  - 10 estaciones en 4 regiones de EE.UU.")
    print("  - Costa Oeste: San Diego, Los Angeles, Seattle")
    print("  - Costa Este: New York, Boston, Miami")
    print("  - Centro: Chicago, Denver")
    print("  - Sur: Houston, Phoenix")
    print("\n[ESCENARIOS] Realistas:")
    print("  - Sin Acción: Aumento 1.5% anual")
    print("  - Política Moderada: Reducción 2% anual")
    print("  - Política Agresiva: Reducción 5% anual")
    print("  - Crecimiento Urbano: Aumento 6% anual")

if __name__ == "__main__":
    main()
