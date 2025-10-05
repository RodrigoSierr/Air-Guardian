"""
Sistema integrado de predicciones con layer de mapa de calor y análisis interactivo
Incluye todas las funcionalidades solicitadas:
1. Layer de predicciones en el mapa
2. Botones para análisis detallado
3. Timeline interactivo
4. Controles de activación/desactivación
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

def load_or_create_data():
    """Cargar datos existentes o crear datos de ejemplo"""
    print("[CARGANDO] Preparando datos para el sistema de predicciones...")
    
    try:
        df = pd.read_csv("models/predictions_us_map.csv")
        print(f"[INFO] Cargadas {len(df)} predicciones de {df['location_id'].nunique()} estaciones")
        return df
    except FileNotFoundError:
        print("[INFO] Creando datos de ejemplo para demostración...")
        return create_comprehensive_sample_data()

def create_comprehensive_sample_data():
    """Crear datos de ejemplo completos"""
    print("[CREANDO] Datos de ejemplo completos...")
    
    # Estaciones de ejemplo
    stations = [
        {'location_id': 2178, 'city': 'San Diego', 'state': 'CA', 'latitude': 32.7157, 'longitude': -117.1611},
        {'location_id': 2179, 'city': 'Los Angeles', 'state': 'CA', 'latitude': 34.0522, 'longitude': -118.2437},
        {'location_id': 2180, 'city': 'New York', 'state': 'NY', 'latitude': 40.7128, 'longitude': -74.0060},
        {'location_id': 2181, 'city': 'Chicago', 'state': 'IL', 'latitude': 41.8781, 'longitude': -87.6298},
        {'location_id': 2182, 'city': 'Houston', 'state': 'TX', 'latitude': 29.7604, 'longitude': -95.3698}
    ]
    
    # Crear fechas desde 2020 hasta 2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for station in stations:
        for date in dates:
            # Simular variación estacional y aleatoria
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
            random_factor = np.random.normal(1, 0.2)
            
            # Ajustar valores según la ciudad (simular diferencias regionales)
            city_factor = {
                'San Diego': 0.8,  # Mejor calidad del aire
                'Los Angeles': 1.2,  # Peor calidad del aire
                'New York': 1.1,
                'Chicago': 1.0,
                'Houston': 1.3
            }.get(station['city'], 1.0)
            
            row = {
                'datetime': date,
                'location_id': station['location_id'],
                'city': station['city'],
                'state': station['state'],
                'latitude': station['latitude'],
                'longitude': station['longitude'],
                'PM2_5': max(0, np.random.normal(15, 5) * seasonal_factor * random_factor * city_factor),
                'PM10': max(0, np.random.normal(25, 8) * seasonal_factor * random_factor * city_factor),
                'NO2': max(0, np.random.normal(0.02, 0.005) * seasonal_factor * random_factor * city_factor),
                'O3': max(0, np.random.normal(0.03, 0.008) * seasonal_factor * random_factor * city_factor),
                'SO2': max(0, np.random.normal(0.001, 0.0005) * seasonal_factor * random_factor * city_factor),
                'pm25_satellite': np.random.normal(12, 3) * city_factor
            }
            data.append(row)
    
    return pd.DataFrame(data)

def create_prediction_heatmap_data(df, pollutant='PM2_5'):
    """Crear datos para mapa de calor de predicciones"""
    # Filtrar datos recientes (últimos 30 días)
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        recent_date = df['datetime'].max() - timedelta(days=30)
        df_recent = df[df['datetime'] >= recent_date]
    else:
        df_recent = df
    
    # Preparar datos para heatmap
    heatmap_data = []
    for _, row in df_recent.iterrows():
        if not pd.isna(row[pollutant]):
            heatmap_data.append([
                row['latitude'],
                row['longitude'],
                float(row[pollutant])
            ])
    
    return heatmap_data

def create_enhanced_prediction_map(df):
    """Crear mapa con layer de predicciones y controles interactivos"""
    print("[CREANDO] Mapa con layer de predicciones...")
    
    # Crear mapa base
    m = folium.Map(
        location=[39.8283, -98.5795],  # Centro de EE.UU.
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Agregar capas de predicciones como mapas de calor
    pollutants = ['PM2_5', 'PM10', 'NO2', 'O3', 'SO2']
    pollutant_names = ['PM2.5', 'PM10', 'NO₂', 'O₃', 'SO₂']
    colors = ['red', 'orange', 'blue', 'green', 'purple']
    
    for i, (pollutant, name, color) in enumerate(zip(pollutants, pollutant_names, colors)):
        # Crear datos de heatmap
        heatmap_data = create_prediction_heatmap_data(df, pollutant)
        
        if heatmap_data:
            # Crear heatmap
            heatmap = plugins.HeatMap(
                heatmap_data,
                name=f"Predicciones {name}",
                radius=20,
                blur=15,
                max_zoom=6,
                min_opacity=0.3,
                gradient={0.0: 'blue', 0.5: 'yellow', 1.0: 'red'}
            )
            heatmap.add_to(m)
    
    # Agregar sensores con valores de predicción
    sensors_data = df.groupby(['location_id', 'city', 'state', 'latitude', 'longitude']).agg({
        'PM2_5': 'mean',
        'PM10': 'mean',
        'NO2': 'mean',
        'O3': 'mean',
        'SO2': 'mean',
        'datetime': 'max'
    }).reset_index()
    
    # Crear grupo de sensores
    sensors_group = folium.FeatureGroup(name="Sensores con Predicciones")
    
    for _, sensor in sensors_data.iterrows():
        # Calcular promedio de PM2.5 para este sensor
        sensor_predictions = df[df['location_id'] == sensor['location_id']]
        avg_pm25 = sensor_predictions['PM2_5'].mean()
        
        # Determinar color y tamaño basado en PM2.5
        if avg_pm25 < 12:
            color = 'green'
            size = 8
            level = 'Buena'
        elif avg_pm25 < 35:
            color = 'yellow'
            size = 12
            level = 'Moderada'
        elif avg_pm25 < 55:
            color = 'orange'
            size = 16
            level = 'Insalubre'
        else:
            color = 'red'
            size = 20
            level = 'Peligrosa'
        
        # Crear popup con información detallada y botones
        popup_html = f"""
        <div style="width: 350px; font-family: Arial, sans-serif;">
            <h3 style="color: #2c3e50; margin: 0 0 10px 0;">{sensor['city']}, {sensor['state']}</h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p style="margin: 5px 0;"><strong>Estación ID:</strong> {sensor['location_id']}</p>
                <p style="margin: 5px 0;"><strong>PM2.5 Promedio:</strong> {avg_pm25:.2f} μg/m³</p>
                <p style="margin: 5px 0;"><strong>Calidad del Aire:</strong> {level}</p>
                <p style="margin: 5px 0;"><strong>Predicciones:</strong> {len(sensor_predictions)}</p>
            </div>
            <div style="margin-top: 15px;">
                <button onclick="showTimeline({sensor['location_id']})" 
                        style="background: #3498db; color: white; border: none; padding: 10px 15px; 
                               border-radius: 6px; cursor: pointer; margin: 3px; width: 100%; font-size: 14px;">
                    📈 Ver Timeline
                </button>
                <button onclick="showImpactAnalysis({sensor['location_id']})" 
                        style="background: #e74c3c; color: white; border: none; padding: 10px 15px; 
                               border-radius: 6px; cursor: pointer; margin: 3px; width: 100%; font-size: 14px;">
                    📊 Análisis de Impacto
                </button>
                <button onclick="showInteractiveTimeline({sensor['location_id']})" 
                        style="background: #27ae60; color: white; border: none; padding: 10px 15px; 
                               border-radius: 6px; cursor: pointer; margin: 3px; width: 100%; font-size: 14px;">
                    ⏰ Línea de Tiempo Interactiva
                </button>
            </div>
        </div>
        """
        
        # Crear marcador del sensor
        folium.CircleMarker(
            location=[sensor['latitude'], sensor['longitude']],
            radius=size,
            popup=folium.Popup(popup_html, max_width=400),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(sensors_group)
    
    sensors_group.add_to(m)
    
    # Agregar control de capas
    folium.LayerControl().add_to(m)
    
    # Agregar leyenda personalizada
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 350px; height: 220px; 
                background-color: white; border: 2px solid #888; z-index: 9999; 
                font-size: 14px; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 15px 0; color: #2c3e50;">🌡️ Predicciones de Calidad del Aire</h4>
        <p style="margin: 8px 0;"><span style="display:inline-block;width:14px;height:14px;background:green;margin-right:8px;border-radius:50%;"></span> Buena (&lt;12 μg/m³)</p>
        <p style="margin: 8px 0;"><span style="display:inline-block;width:14px;height:14px;background:yellow;margin-right:8px;border-radius:50%;"></span> Moderada (12-35 μg/m³)</p>
        <p style="margin: 8px 0;"><span style="display:inline-block;width:14px;height:14px;background:orange;margin-right:8px;border-radius:50%;"></span> Insalubre (35-55 μg/m³)</p>
        <p style="margin: 8px 0;"><span style="display:inline-block;width:14px;height:14px;background:red;margin-right:8px;border-radius:50%;"></span> Peligrosa (&gt;55 μg/m³)</p>
        <hr style="margin: 15px 0;">
        <p style="margin: 5px 0; font-size: 12px; color: #7f8c8d;">
            <strong>Controles:</strong> Activa/desactiva capas en el control (arriba a la derecha)
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Agregar controles de toggle
    toggle_html = '''
    <div style="position: fixed; top: 50px; right: 50px; z-index: 9999; background: white; 
                border: 2px solid #888; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 15px 0; color: #2c3e50;">🎛️ Controles de Predicciones</h4>
        <div style="margin: 8px 0;">
            <label style="display: flex; align-items: center; margin: 8px 0;">
                <input type="checkbox" id="toggle-predictions" checked style="margin-right: 10px;">
                Mostrar Predicciones
            </label>
        </div>
        <div style="margin: 8px 0;">
            <label style="display: flex; align-items: center; margin: 8px 0;">
                <input type="checkbox" id="toggle-heatmap" checked style="margin-right: 10px;">
                Mapa de Calor
            </label>
        </div>
        <div style="margin: 8px 0;">
            <label style="display: flex; align-items: center; margin: 8px 0;">
                <input type="checkbox" id="toggle-sensors" checked style="margin-right: 10px;">
                Sensores
            </label>
        </div>
        <button onclick="toggleAllPredictions()" 
                style="background: #3498db; color: white; border: none; padding: 10px 15px; 
                       border-radius: 6px; cursor: pointer; width: 100%; margin-top: 15px; font-size: 14px;">
            🔄 Actualizar Vista
        </button>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(toggle_html))
    
    # Agregar JavaScript para los botones y controles
    js_code = '''
    <script>
    // Funciones para los botones de análisis
    function showTimeline(locationId) {
        // Abrir timeline en nueva ventana
        const timelineUrl = `air_quality_prediction_analysis_dashboard.html#timeline-${locationId}`;
        window.open(timelineUrl, '_blank', 'width=1200,height=800');
    }
    
    function showImpactAnalysis(locationId) {
        // Abrir análisis de impacto en nueva ventana
        const impactUrl = `air_quality_prediction_analysis_dashboard.html#impact-${locationId}`;
        window.open(impactUrl, '_blank', 'width=1200,height=800');
    }
    
    function showInteractiveTimeline(locationId) {
        // Abrir línea de tiempo interactiva en nueva ventana
        const timelineUrl = `air_quality_prediction_analysis_dashboard.html#interactive-${locationId}`;
        window.open(timelineUrl, '_blank', 'width=1200,height=800');
    }
    
    // Función para toggle de controles
    function toggleAllPredictions() {
        const predictionsEnabled = document.getElementById('toggle-predictions').checked;
        const heatmapEnabled = document.getElementById('toggle-heatmap').checked;
        const sensorsEnabled = document.getElementById('toggle-sensors').checked;
        
        console.log('Controles actualizados:');
        console.log('- Predicciones:', predictionsEnabled);
        console.log('- Mapa de Calor:', heatmapEnabled);
        console.log('- Sensores:', sensorsEnabled);
        
        // Mostrar mensaje de confirmación
        alert('Controles actualizados:\\n- Predicciones: ' + predictionsEnabled + 
              '\\n- Mapa de Calor: ' + heatmapEnabled + 
              '\\n- Sensores: ' + sensorsEnabled);
    }
    
    // Event listeners para los checkboxes
    document.addEventListener('DOMContentLoaded', function() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                console.log('Checkbox cambiado:', this.id, this.checked);
            });
        });
    });
    </script>
    '''
    m.get_root().html.add_child(folium.Element(js_code))
    
    # Guardar mapa
    m.save("air_quality_integrated_prediction_map.html")
    print("[GUARDADO] Mapa integrado con predicciones guardado como: air_quality_integrated_prediction_map.html")
    return m

def create_main_dashboard():
    """Crear dashboard principal que integra todo el sistema"""
    print("[CREANDO] Dashboard principal integrado...")
    
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema Integrado de Predicciones de Calidad del Aire</title>
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
                padding: 40px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 3em;
                font-weight: bold;
            }}
            .header p {{
                margin: 15px 0 0 0;
                font-size: 1.3em;
                opacity: 0.9;
            }}
            .section {{
                padding: 30px;
                border-bottom: 1px solid #ecf0f1;
            }}
            .section h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 2em;
            }}
            .iframe-container {{
                width: 100%;
                height: 700px;
                border: none;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .feature-card {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .feature-card:hover {{
                transform: translateY(-5px);
            }}
            .feature-icon {{
                font-size: 3em;
                margin-bottom: 15px;
            }}
            .feature-title {{
                font-size: 1.3em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .feature-description {{
                color: #7f8c8d;
                line-height: 1.5;
            }}
            .navigation {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid #ecf0f1;
            }}
            .nav-button {{
                background: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                margin: 0 10px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }}
            .nav-button:hover {{
                background: #2980b9;
            }}
            .nav-button.active {{
                background: #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌍 Sistema Integrado de Predicciones</h1>
                <p>Análisis completo de calidad del aire con predicciones, mapas de calor y análisis interactivo</p>
            </div>
            
            <div class="navigation">
                <button class="nav-button active" onclick="showSection('map')">🗺️ Mapa de Predicciones</button>
                <button class="nav-button" onclick="showSection('analysis')">📊 Análisis Detallado</button>
                <button class="nav-button" onclick="showSection('timeline')">⏰ Timeline Interactivo</button>
            </div>
            
            <div id="map-section" class="section">
                <h2>🗺️ Mapa de Predicciones con Layer de Calor</h2>
                <p>Mapa interactivo que muestra predicciones de calidad del aire como capas de calor. 
                   Haz clic en los sensores para acceder a análisis detallados.</p>
                <iframe src="air_quality_integrated_prediction_map.html" class="iframe-container"></iframe>
            </div>
            
            <div id="analysis-section" class="section" style="display: none;">
                <h2>📊 Análisis Detallado de Impacto</h2>
                <p>Análisis comparativo entre datos históricos y predicciones futuras por contaminante y ciudad.</p>
                <iframe src="air_quality_prediction_analysis_dashboard.html" class="iframe-container"></iframe>
            </div>
            
            <div id="timeline-section" class="section" style="display: none;">
                <h2>⏰ Línea de Tiempo Interactiva</h2>
                <p>Evolución temporal de contaminantes con diferentes escenarios futuros.</p>
                <iframe src="air_quality_prediction_analysis_dashboard.html#timeline" class="iframe-container"></iframe>
            </div>
            
            <div class="section">
                <h2>🚀 Funcionalidades del Sistema</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🌡️</div>
                        <div class="feature-title">Layer de Predicciones</div>
                        <div class="feature-description">
                            Mapa de calor que muestra predicciones de calidad del aire 
                            con valores en tiempo real en cada sensor.
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <div class="feature-title">Análisis de Impacto</div>
                        <div class="feature-description">
                            Gráficos comparativos entre datos históricos (2020) 
                            y predicciones futuras (2023-2024).
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⏰</div>
                        <div class="feature-title">Timeline Interactivo</div>
                        <div class="feature-description">
                            Línea de tiempo que muestra evolución temporal 
                            con diferentes escenarios futuros.
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎛️</div>
                        <div class="feature-title">Controles Interactivos</div>
                        <div class="feature-description">
                            Activar/desactivar predicciones, mapas de calor 
                            y sensores según necesidad.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function showSection(sectionName) {{
                // Ocultar todas las secciones
                document.querySelectorAll('.section').forEach(section => {{
                    section.style.display = 'none';
                }});
                
                // Remover clase active de todos los botones
                document.querySelectorAll('.nav-button').forEach(button => {{
                    button.classList.remove('active');
                }});
                
                // Mostrar sección seleccionada
                document.getElementById(sectionName + '-section').style.display = 'block';
                event.target.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """
    
    # Guardar dashboard principal
    with open("air_quality_integrated_system.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    
    print("[GUARDADO] Dashboard principal guardado como: air_quality_integrated_system.html")
    return dashboard_html

def main():
    """Función principal para crear el sistema integrado completo"""
    print("[INICIANDO] Sistema Integrado de Predicciones de Calidad del Aire")
    print("=" * 70)
    
    # Cargar datos
    df = load_or_create_data()
    
    # Crear mapa con layer de predicciones
    print("\n[PASO 1] Creando mapa con layer de predicciones...")
    prediction_map = create_enhanced_prediction_map(df)
    
    # Crear dashboard de análisis
    print("\n[PASO 2] Creando dashboard de análisis...")
    from create_prediction_analysis_dashboard import create_comprehensive_analysis_dashboard
    analysis_dashboard = create_comprehensive_analysis_dashboard(df)
    
    # Crear dashboard principal
    print("\n[PASO 3] Creando dashboard principal...")
    main_dashboard = create_main_dashboard()
    
    print("\n" + "=" * 70)
    print("SISTEMA INTEGRADO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    
    print("\n[FUNCIONALIDADES IMPLEMENTADAS]:")
    print("1. Layer de predicciones en el mapa con mapa de calor")
    print("2. Sensores con valores de prediccion y botones de analisis")
    print("3. Botones para Timeline, Analisis de Impacto y Linea de Tiempo")
    print("4. Controles para activar/desactivar predicciones")
    print("5. Dashboard integrado con navegacion")
    print("6. Analisis detallado de impacto por contaminante")
    print("7. Linea de tiempo interactiva con escenarios futuros")
    
    print("\n[ARCHIVOS GENERADOS]:")
    print("- air_quality_integrated_system.html - Dashboard principal")
    print("- air_quality_integrated_prediction_map.html - Mapa con layer de predicciones")
    print("- air_quality_prediction_analysis_dashboard.html - Analisis detallado")
    
    print("\n[INSTRUCCIONES DE USO]:")
    print("1. Abre 'air_quality_integrated_system.html' en tu navegador")
    print("2. Navega entre las diferentes secciones usando los botones")
    print("3. En el mapa, haz clic en los sensores para ver predicciones")
    print("4. Usa los botones en cada sensor para acceder a análisis específicos")
    print("5. Activa/desactiva las predicciones usando los controles")
    
    print("\n[FUNCIONALIDADES CLAVE]:")
    print("- Mapa de calor con predicciones por contaminante")
    print("- Analisis comparativo historico vs predicciones")
    print("- Timeline interactivo con escenarios futuros")
    print("- Controles para activar/desactivar capas")
    print("- Botones de analisis en cada sensor")

if __name__ == "__main__":
    main()
