"""
Visualización interactiva de predicciones de calidad del aire en mapa de EE.UU.
Incluye línea de tiempo y proyecciones futuras.
"""
import pandas as pd
import numpy as np
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

def load_predictions():
    """Cargar las predicciones generadas"""
    print("[CARGANDO] Leyendo archivo de predicciones...")
    df = pd.read_csv("models/predictions_us_map.csv")
    print(f"[INFO] Cargadas {len(df)} predicciones de {df['location_id'].nunique()} estaciones")
    return df

def create_static_map(df):
    """Crear mapa estático con todas las estaciones"""
    print("[CREANDO] Mapa estático de estaciones...")
    
    # Obtener coordenadas únicas de las estaciones
    stations = df.groupby(['location_id', 'city', 'state', 'latitude', 'longitude']).size().reset_index(name='predicciones')
    
    # Crear mapa centrado en EE.UU.
    m = folium.Map(
        location=[39.8283, -98.5795],  # Centro de EE.UU.
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Agregar marcadores para cada estación
    for _, station in stations.iterrows():
        # Calcular promedio de PM2.5 para esta estación
        station_data = df[df['location_id'] == station['location_id']]
        avg_pm25 = station_data['PM2_5'].mean()
        
        # Color basado en nivel de PM2.5
        if avg_pm25 < 12:
            color = 'green'
            level = 'Buena'
        elif avg_pm25 < 35:
            color = 'yellow'
            level = 'Moderada'
        elif avg_pm25 < 55:
            color = 'orange'
            level = 'Insalubre para grupos sensibles'
        else:
            color = 'red'
            level = 'Insalubre'
        
        # Crear popup con información
        popup_text = f"""
        <b>{station['city']}, {station['state']}</b><br>
        <b>Estación ID:</b> {station['location_id']}<br>
        <b>PM2.5 Promedio:</b> {avg_pm25:.2f} μg/m³<br>
        <b>Calidad del Aire:</b> {level}<br>
        <b>Predicciones:</b> {station['predicciones']}
        """
        
        folium.CircleMarker(
            location=[station['latitude'], station['longitude']],
            radius=10,
            popup=folium.Popup(popup_text, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    # Agregar leyenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Calidad del Aire (PM2.5)</b></p>
    <p><i class="fa fa-circle" style="color:green"></i> Buena (&lt;12)</p>
    <p><i class="fa fa-circle" style="color:yellow"></i> Moderada (12-35)</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Insalubre (35-55)</p>
    <p><i class="fa fa-circle" style="color:red"></i> Peligrosa (&gt;55)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar mapa
    m.save("air_quality_stations_map.html")
    print("[GUARDADO] Mapa guardado como: air_quality_stations_map.html")
    return m

def create_timeline_visualization(df):
    """Crear visualización temporal de la evolución de la contaminación"""
    print("[CREANDO] Visualización temporal...")
    
    # Convertir datetime si es necesario
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    else:
        # Crear fechas simuladas para el ejemplo
        start_date = datetime.datetime(2020, 1, 1)
        df['datetime'] = [start_date + timedelta(hours=i) for i in range(len(df))]
    
    # Agrupar por fecha y calcular promedios
    daily_avg = df.groupby('datetime').agg({
        'PM2_5': 'mean',
        'PM10': 'mean',
        'NO2': 'mean',
        'O3': 'mean',
        'SO2': 'mean'
    }).reset_index()
    
    # Crear gráfico de líneas múltiples
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('PM2.5 (μg/m³)', 'PM10 (μg/m³)', 'NO₂ (ppm)', 'O₃ (ppm)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # PM2.5
    fig.add_trace(
        go.Scatter(x=daily_avg['datetime'], y=daily_avg['PM2_5'], 
                  name='PM2.5', line=dict(color='red', width=2)),
        row=1, col=1
    )
    
    # PM10
    fig.add_trace(
        go.Scatter(x=daily_avg['datetime'], y=daily_avg['PM10'], 
                  name='PM10', line=dict(color='orange', width=2)),
        row=1, col=2
    )
    
    # NO2
    fig.add_trace(
        go.Scatter(x=daily_avg['datetime'], y=daily_avg['NO2'], 
                  name='NO₂', line=dict(color='blue', width=2)),
        row=2, col=1
    )
    
    # O3
    fig.add_trace(
        go.Scatter(x=daily_avg['datetime'], y=daily_avg['O3'], 
                  name='O₃', line=dict(color='green', width=2)),
        row=2, col=2
    )
    
    # Actualizar layout
    fig.update_layout(
        title='Evolución Temporal de Contaminantes del Aire - San Diego, CA',
        height=600,
        showlegend=True,
        template='plotly_white'
    )
    
    # Guardar gráfico
    fig.write_html("air_quality_timeline.html")
    print("[GUARDADO] Timeline guardado como: air_quality_timeline.html")
    return fig

def create_future_projections(df):
    """Crear proyecciones futuras con diferentes escenarios"""
    print("[CREANDO] Proyecciones futuras...")
    
    # Obtener datos de la última fecha disponible
    last_date = df['datetime'].max() if 'datetime' in df.columns else datetime.datetime(2020, 12, 31)
    
    # Crear fechas futuras (próximos 30 días)
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    
    # Obtener promedios actuales por estación
    station_avg = df.groupby('location_id').agg({
        'PM2_5': 'mean',
        'PM10': 'mean',
        'NO2': 'mean',
        'O3': 'mean',
        'SO2': 'mean',
        'latitude': 'first',
        'longitude': 'first',
        'city': 'first',
        'state': 'first'
    }).reset_index()
    
    # Crear escenarios
    scenarios = {
        'Tendencia Actual': 1.0,
        'Reducción 20%': 0.8,
        'Aumento 20%': 1.2,
        'Reducción 50%': 0.5
    }
    
    # Crear mapa interactivo con escenarios
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Agregar capas para cada escenario
    for scenario, factor in scenarios.items():
        feature_group = folium.FeatureGroup(name=scenario)
        
        for _, station in station_avg.iterrows():
            # Aplicar factor de escenario
            pm25_projected = station['PM2_5'] * factor
            
            # Color basado en PM2.5 proyectado
            if pm25_projected < 12:
                color = 'green'
            elif pm25_projected < 35:
                color = 'yellow'
            elif pm25_projected < 55:
                color = 'orange'
            else:
                color = 'red'
            
            # Crear marcador
            folium.CircleMarker(
                location=[station['latitude'], station['longitude']],
                radius=8,
                popup=f"""
                <b>{station['city']}, {station['state']}</b><br>
                <b>Escenario:</b> {scenario}<br>
                <b>PM2.5 Proyectado:</b> {pm25_projected:.2f} μg/m³
                """,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(feature_group)
        
        feature_group.add_to(m)
    
    # Agregar control de capas
    folium.LayerControl().add_to(m)
    
    # Guardar mapa de escenarios
    m.save("air_quality_scenarios_map.html")
    print("[GUARDADO] Mapa de escenarios guardado como: air_quality_scenarios_map.html")
    return m

def create_dashboard():
    """Crear dashboard completo con todas las visualizaciones"""
    print("[INICIANDO] Creación de dashboard completo...")
    
    # Cargar datos
    df = load_predictions()
    
    # Crear visualizaciones
    static_map = create_static_map(df)
    timeline = create_timeline_visualization(df)
    scenarios_map = create_future_projections(df)
    
    # Crear dashboard HTML
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Calidad del Aire - EE.UU.</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .section {{
                background-color: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .iframe-container {{
                width: 100%;
                height: 600px;
                border: none;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                text-align: center;
            }}
            .stat {{
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌍 Dashboard de Calidad del Aire - EE.UU.</h1>
            <p>Predicciones basadas en datos de OpenAQ y NASA EarthData</p>
        </div>
        
        <div class="section">
            <h2>📊 Estadísticas Generales</h2>
            <div class="stats">
                <div class="stat">
                    <h3>{df['location_id'].nunique()}</h3>
                    <p>Estaciones Procesadas</p>
                </div>
                <div class="stat">
                    <h3>{len(df):,}</h3>
                    <p>Predicciones Generadas</p>
                </div>
                <div class="stat">
                    <h3>{df['PM2_5'].mean():.2f}</h3>
                    <p>PM2.5 Promedio (μg/m³)</p>
                </div>
                <div class="stat">
                    <h3>{df['city'].iloc[0]}, {df['state'].iloc[0]}</h3>
                    <p>Ciudad Principal</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🗺️ Mapa de Estaciones</h2>
            <iframe src="air_quality_stations_map.html" class="iframe-container"></iframe>
        </div>
        
        <div class="section">
            <h2>📈 Evolución Temporal</h2>
            <iframe src="air_quality_timeline.html" class="iframe-container"></iframe>
        </div>
        
        <div class="section">
            <h2>🔮 Escenarios Futuros</h2>
            <iframe src="air_quality_scenarios_map.html" class="iframe-container"></iframe>
        </div>
        
        <div class="section">
            <h2>ℹ️ Información del Proyecto</h2>
            <p><strong>Objetivo:</strong> Predecir niveles de contaminación atmosférica combinando datos de sensores urbanos (OpenAQ) y datos satelitales (NASA EarthData).</p>
            <p><strong>Contaminantes:</strong> PM2.5, PM10, NO₂, O₃, SO₂</p>
            <p><strong>Modelo:</strong> Random Forest Regressor con validación temporal</p>
            <p><strong>Datos:</strong> Estación 2178 - San Diego, CA (2020)</p>
        </div>
    </body>
    </html>
    """
    
    with open("air_quality_dashboard.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    
    print("[COMPLETADO] Dashboard creado como: air_quality_dashboard.html")
    print("\n[ARCHIVOS GENERADOS]:")
    print("  - air_quality_dashboard.html (Dashboard principal)")
    print("  - air_quality_stations_map.html (Mapa de estaciones)")
    print("  - air_quality_timeline.html (Evolución temporal)")
    print("  - air_quality_scenarios_map.html (Escenarios futuros)")

if __name__ == "__main__":
    create_dashboard()
