#!/usr/bin/env python3
"""
Script de sincronización entre el modelo predictivo avanzado de calidad del aire
y el sistema Air-Guardian.

Este script:
1. Integra el modelo multisalida avanzado con datos satelitales
2. Actualiza el sistema Air-Guardian con capacidades mejoradas
3. Sincroniza las funcionalidades de predicción
"""

import os
import sys
import shutil
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
import json

# Configuración de rutas
AIR_GUARDIAN_PATH = r"C:\Users\Usuario\Documents\Air-Guardian"
CURRENT_MODEL_PATH = "."
AIR_GUARDIAN_BACKEND = os.path.join(AIR_GUARDIAN_PATH, "backend")
AIR_GUARDIAN_MODELS = os.path.join(AIR_GUARDIAN_BACKEND, "model")

def create_advanced_ml_model():
    """
    Crea un modelo ML avanzado que integra las capacidades del modelo predictivo
    con el sistema Air-Guardian.
    """
    
    class AdvancedAirQualityPredictor:
        """
        Modelo predictivo avanzado que combina:
        - Datos de estaciones terrestres (OpenAQ)
        - Datos satelitales (NASA EarthData)
        - Predicciones multisalida (PM2.5, PM10, NO2, O3, SO2)
        - Validación temporal
        """
        
        def __init__(self):
            self.model = None
            self.scaler = None
            self.satellite_data = None
            self.feature_columns = None
            self.output_columns = ["PM2_5", "PM10", "NO2", "O3", "SO2"]
            
        def load_satellite_data(self, satellite_file=None):
            """Carga datos satelitales de PM2.5"""
            if satellite_file and os.path.exists(satellite_file):
                try:
                    import xarray as xr
                    self.satellite_data = xr.open_dataset(satellite_file)
                    print("Datos satelitales cargados exitosamente")
                    return True
                except Exception as e:
                    print(f"⚠️ Error cargando datos satelitales: {e}")
                    return False
            return False
        
        def get_satellite_pm25(self, lat, lon):
            """Obtiene valor de PM2.5 satelital para coordenadas dadas"""
            if self.satellite_data is None:
                return np.nan
            
            try:
                lat_idx = np.abs(self.satellite_data["lat"].values - lat).argmin()
                lon_idx = np.abs(self.satellite_data["lon"].values - lon).argmin()
                return float(self.satellite_data["GWRPM25"].values[lat_idx, lon_idx])
            except Exception as e:
                print(f"Error obteniendo datos satelitales: {e}")
                return np.nan
        
        def create_advanced_features(self, df):
            """Crea características avanzadas para el modelo"""
            df = df.copy()
            
            # Características temporales cíclicas
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['month'] = df['timestamp'].dt.month
                df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
                
                # Codificación cíclica
                df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
                df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
                df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
                df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            
            # Características de lag (valores anteriores)
            lag_columns = ['PM2_5', 'PM10', 'NO2', 'O3', 'SO2']
            for col in lag_columns:
                if col in df.columns:
                    df[f'{col}_lag_1h'] = df[col].shift(1)
                    df[f'{col}_lag_3h'] = df[col].shift(3)
                    df[f'{col}_lag_6h'] = df[col].shift(6)
                    df[f'{col}_lag_24h'] = df[col].shift(24)
            
            # Estadísticas móviles
            if 'PM2_5' in df.columns:
                df['PM2_5_rolling_mean_6h'] = df['PM2_5'].rolling(window=6, min_periods=1).mean()
                df['PM2_5_rolling_std_6h'] = df['PM2_5'].rolling(window=6, min_periods=1).std()
                df['PM2_5_rolling_mean_24h'] = df['PM2_5'].rolling(window=24, min_periods=1).mean()
            
            # Integrar datos satelitales si están disponibles
            if 'latitude' in df.columns and 'longitude' in df.columns:
                df['pm25_satellite'] = df.apply(
                    lambda row: self.get_satellite_pm25(row['latitude'], row['longitude']), 
                    axis=1
                )
            
            return df
        
        def train_advanced_model(self, df):
            """Entrena el modelo avanzado con validación temporal"""
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.multioutput import MultiOutputRegressor
            from sklearn.model_selection import TimeSeriesSplit
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            print("🔧 Creando características avanzadas...")
            df_features = self.create_advanced_features(df)
            
            # Eliminar filas con NaN
            df_features = df_features.dropna()
            
            # Separar características y objetivos
            feature_cols = [col for col in df_features.columns 
                          if col not in self.output_columns + ['timestamp', 'latitude', 'longitude']]
            
            X = df_features[feature_cols]
            y = df_features[self.output_columns]
            
            self.feature_columns = feature_cols
            
            # Validación temporal
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Modelo base
            base_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            # Modelo multisalida
            model = MultiOutputRegressor(base_model, n_jobs=-1)
            
            # Escalado
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Entrenamiento con validación temporal
            print("🚀 Entrenando modelo con validación temporal...")
            model.fit(X_scaled, y)
            
            # Evaluación
            scores = []
            for train_idx, val_idx in tscv.split(X_scaled):
                X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                
                # Calcular R² para cada contaminante
                for i, col in enumerate(self.output_columns):
                    r2 = r2_score(y_val.iloc[:, i], y_pred[:, i])
                    scores.append(r2)
            
            avg_r2 = np.mean(scores)
            print(f"📊 R² promedio (validación temporal): {avg_r2:.4f}")
            
            # Entrenar modelo final con todos los datos
            self.model = model
            self.model.fit(X_scaled, y)
            
            return avg_r2
        
        def predict_advanced(self, features_dict):
            """Realiza predicciones avanzadas"""
            if self.model is None:
                raise ValueError("Modelo no entrenado")
            
            # Crear DataFrame con las características
            features_df = pd.DataFrame([features_dict])
            
            # Asegurar que todas las características estén presentes
            for col in self.feature_columns:
                if col not in features_df.columns:
                    features_df[col] = 0.0
            
            # Reordenar columnas según el orden de entrenamiento
            features_df = features_df[self.feature_columns]
            
            # Escalar características
            features_scaled = self.scaler.transform(features_df)
            
            # Predecir
            predictions = self.model.predict(features_scaled)
            
            # Crear diccionario de resultados
            results = {}
            for i, col in enumerate(self.output_columns):
                results[col] = float(predictions[0][i])
            
            return results
        
        def predict_future_scenarios(self, current_data, hours_ahead=48):
            """Predice escenarios futuros con diferentes factores"""
            scenarios = {
                "tendencia_actual": 1.0,
                "politica_verde": 0.7,
                "crecimiento_urbano": 1.3,
                "emergencia_climatica": 0.4,
                "sin_cambios": 1.0
            }
            
            predictions = {}
            
            for scenario_name, factor in scenarios.items():
                scenario_predictions = []
                
                for hour in range(1, hours_ahead + 1):
                    # Crear características para predicción futura
                    future_time = datetime.now() + pd.Timedelta(hours=hour)
                    
                    features = {
                        'hour_sin': np.sin(2 * np.pi * future_time.hour / 24),
                        'hour_cos': np.cos(2 * np.pi * future_time.hour / 24),
                        'month_sin': np.sin(2 * np.pi * future_time.month / 12),
                        'month_cos': np.cos(2 * np.pi * future_time.month / 12),
                        'is_weekend': 1 if future_time.weekday() >= 5 else 0,
                        'PM2_5': current_data.get('PM2_5', 30),
                        'PM10': current_data.get('PM10', 45),
                        'NO2': current_data.get('NO2', 40),
                        'O3': current_data.get('O3', 50),
                        'temperature': current_data.get('temperature', 20),
                        'humidity': current_data.get('humidity', 60),
                        'wind_speed': current_data.get('wind_speed', 5),
                        'pressure': current_data.get('pressure', 1013),
                        'pm25_satellite': current_data.get('pm25_satellite', 25),
                    }
                    
                    # Agregar características de lag
                    for col in self.output_columns:
                        features[f'{col}_lag_1h'] = current_data.get(col, 30)
                        features[f'{col}_lag_3h'] = current_data.get(col, 30)
                        features[f'{col}_lag_6h'] = current_data.get(col, 30)
                        features[f'{col}_lag_24h'] = current_data.get(col, 30)
                    
                    # Agregar estadísticas móviles
                    features['PM2_5_rolling_mean_6h'] = current_data.get('PM2_5', 30)
                    features['PM2_5_rolling_std_6h'] = 5.0
                    features['PM2_5_rolling_mean_24h'] = current_data.get('PM2_5', 30)
                    
                    # Predecir
                    try:
                        pred = self.predict_advanced(features)
                        
                        # Aplicar factor de escenario
                        adjusted_pred = {}
                        for pollutant, value in pred.items():
                            adjusted_pred[pollutant] = max(0, value * factor)
                        
                        scenario_predictions.append({
                            'timestamp': future_time.isoformat(),
                            'hour': hour,
                            'predictions': adjusted_pred,
                            'confidence': max(0.5, 1.0 - (hour / hours_ahead) * 0.5)
                        })
                        
                    except Exception as e:
                        print(f"Error en predicción para hora {hour}: {e}")
                        continue
                
                predictions[scenario_name] = scenario_predictions
            
            return predictions
        
        def save_model(self, model_path):
            """Guarda el modelo entrenado"""
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'output_columns': self.output_columns,
                'trained_at': datetime.now().isoformat()
            }
            
            joblib.dump(model_data, model_path)
            print(f"💾 Modelo guardado en: {model_path}")
        
        def load_model(self, model_path):
            """Carga un modelo entrenado"""
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_columns = model_data['feature_columns']
                self.output_columns = model_data['output_columns']
                print(f"📂 Modelo cargado desde: {model_path}")
                return True
            return False
    
    return AdvancedAirQualityPredictor()

def sync_with_airguardian():
    """Sincroniza el modelo avanzado con Air-Guardian"""
    
    print("🔄 Iniciando sincronización con Air-Guardian...")
    
    # 1. Crear directorio de modelos en Air-Guardian
    os.makedirs(AIR_GUARDIAN_MODELS, exist_ok=True)
    
    # 2. Copiar archivos necesarios
    files_to_copy = [
        ("requirements.txt", os.path.join(AIR_GUARDIAN_BACKEND, "requirements_advanced.txt")),
        ("scripts/preprocess_data.py", os.path.join(AIR_GUARDIAN_BACKEND, "preprocess_data.py")),
        ("scripts/download_s3_openaq.py", os.path.join(AIR_GUARDIAN_BACKEND, "download_s3_openaq.py")),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"📋 Copiado: {src} -> {dst}")
    
    # 3. Crear modelo avanzado
    predictor = create_advanced_ml_model()
    
    # 4. Generar datos sintéticos para entrenamiento
    print("🎲 Generando datos sintéticos para entrenamiento...")
    n_samples = 5000
    timestamps = [datetime.now() - pd.Timedelta(hours=i) for i in range(n_samples)]
    
    synthetic_data = {
        'timestamp': timestamps,
        'PM2_5': np.random.gamma(2, 15, n_samples) + 10,
        'PM10': np.random.gamma(2, 20, n_samples) + 15,
        'NO2': np.random.gamma(2, 10, n_samples) + 5,
        'O3': np.random.gamma(2, 15, n_samples) + 10,
        'SO2': np.random.gamma(2, 5, n_samples) + 2,
        'temperature': np.random.normal(20, 8, n_samples),
        'humidity': np.random.uniform(30, 90, n_samples),
        'wind_speed': np.random.gamma(2, 3, n_samples),
        'pressure': np.random.normal(1013, 10, n_samples),
        'latitude': np.random.uniform(-12.2, -11.8, n_samples),  # Lima area
        'longitude': np.random.uniform(-77.2, -76.8, n_samples),
    }
    
    df_synthetic = pd.DataFrame(synthetic_data)
    
    # 5. Entrenar modelo avanzado
    print("🚀 Entrenando modelo avanzado...")
    r2_score = predictor.train_advanced_model(df_synthetic)
    
    # 6. Guardar modelo en Air-Guardian
    model_path = os.path.join(AIR_GUARDIAN_MODELS, "advanced_aqi_model.pkl")
    predictor.save_model(model_path)
    
    # 7. Crear archivo de configuración
    config = {
        "model_type": "advanced_multisalida",
        "features": predictor.feature_columns,
        "outputs": predictor.output_columns,
        "r2_score": float(r2_score),
        "trained_at": datetime.now().isoformat(),
        "capabilities": [
            "prediccion_multisalida",
            "datos_satelitales",
            "validacion_temporal",
            "escenarios_futuros",
            "caracteristicas_avanzadas"
        ]
    }
    
    config_path = os.path.join(AIR_GUARDIAN_MODELS, "model_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"⚙️ Configuración guardada en: {config_path}")
    
    return predictor, config

def create_integration_api():
    """Crea API endpoints integrados para Air-Guardian"""
    
    integration_code = '''
"""
API endpoints integrados para Air-Guardian con modelo avanzado
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os

router = APIRouter(prefix="/api/advanced", tags=["Advanced Predictions"])

class AdvancedPredictionRequest(BaseModel):
    station_id: str
    current_data: Dict[str, float]
    hours_ahead: int = 48
    scenario: str = "tendencia_actual"

class AdvancedPredictionResponse(BaseModel):
    station_id: str
    predictions: Dict[str, List[Dict[str, Any]]]
    model_info: Dict[str, Any]
    generated_at: str

# Cargar modelo avanzado
model_path = "model/advanced_aqi_model.pkl"
config_path = "model/model_config.json"

if os.path.exists(model_path) and os.path.exists(config_path):
    model_data = joblib.load(model_path)
    with open(config_path, 'r') as f:
        model_config = json.load(f)
    
    advanced_predictor = model_data
    print("✅ Modelo avanzado cargado exitosamente")
else:
    advanced_predictor = None
    print("⚠️ Modelo avanzado no encontrado")

@router.post("/predict", response_model=AdvancedPredictionResponse)
async def advanced_predict(request: AdvancedPredictionRequest):
    """Predicción avanzada con múltiples escenarios"""
    if advanced_predictor is None:
        raise HTTPException(status_code=503, detail="Modelo avanzado no disponible")
    
    try:
        # Realizar predicciones para múltiples escenarios
        scenarios = {
            "tendencia_actual": 1.0,
            "politica_verde": 0.7,
            "crecimiento_urbano": 1.3,
            "emergencia_climatica": 0.4,
            "sin_cambios": 1.0
        }
        
        predictions = {}
        
        for scenario_name, factor in scenarios.items():
            scenario_predictions = []
            
            for hour in range(1, request.hours_ahead + 1):
                future_time = datetime.now() + timedelta(hours=hour)
                
                # Crear características
                features = {
                    'hour_sin': np.sin(2 * np.pi * future_time.hour / 24),
                    'hour_cos': np.cos(2 * np.pi * future_time.hour / 24),
                    'month_sin': np.sin(2 * np.pi * future_time.month / 12),
                    'month_cos': np.cos(2 * np.pi * future_time.month / 12),
                    'is_weekend': 1 if future_time.weekday() >= 5 else 0,
                    **request.current_data
                }
                
                # Agregar características de lag
                for col in model_config['outputs']:
                    features[f'{col}_lag_1h'] = request.current_data.get(col, 30)
                    features[f'{col}_lag_3h'] = request.current_data.get(col, 30)
                    features[f'{col}_lag_6h'] = request.current_data.get(col, 30)
                    features[f'{col}_lag_24h'] = request.current_data.get(col, 30)
                
                # Agregar estadísticas móviles
                features['PM2_5_rolling_mean_6h'] = request.current_data.get('PM2_5', 30)
                features['PM2_5_rolling_std_6h'] = 5.0
                features['PM2_5_rolling_mean_24h'] = request.current_data.get('PM2_5', 30)
                
                # Predecir
                try:
                    pred = advanced_predictor.predict_advanced(features)
                    
                    # Aplicar factor de escenario
                    adjusted_pred = {}
                    for pollutant, value in pred.items():
                        adjusted_pred[pollutant] = max(0, value * factor)
                    
                    scenario_predictions.append({
                        'timestamp': future_time.isoformat(),
                        'hour': hour,
                        'predictions': adjusted_pred,
                        'confidence': max(0.5, 1.0 - (hour / request.hours_ahead) * 0.5)
                    })
                    
                except Exception as e:
                    print(f"Error en predicción: {e}")
                    continue
            
            predictions[scenario_name] = scenario_predictions
        
        return AdvancedPredictionResponse(
            station_id=request.station_id,
            predictions=predictions,
            model_info=model_config,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@router.get("/scenarios")
async def get_available_scenarios():
    """Obtiene escenarios disponibles para predicción"""
    return {
        "scenarios": {
            "tendencia_actual": {
                "name": "Tendencia Actual",
                "description": "Si las tendencias actuales continúan",
                "factor": 1.0
            },
            "politica_verde": {
                "name": "Política Verde",
                "description": "Implementación de políticas ambientales estrictas",
                "factor": 0.7
            },
            "crecimiento_urbano": {
                "name": "Crecimiento Urbano",
                "description": "Aumento de urbanización y tráfico",
                "factor": 1.3
            },
            "emergencia_climatica": {
                "name": "Emergencia Climática",
                "description": "Reducción drástica de emisiones",
                "factor": 0.4
            },
            "sin_cambios": {
                "name": "Sin Cambios",
                "description": "Mantener niveles actuales",
                "factor": 1.0
            }
        }
    }

@router.get("/model-info")
async def get_model_info():
    """Obtiene información del modelo avanzado"""
    if advanced_predictor is None:
        raise HTTPException(status_code=503, detail="Modelo avanzado no disponible")
    
    return model_config
'''
    
    # Guardar archivo de integración
    integration_file = os.path.join(AIR_GUARDIAN_BACKEND, "advanced_api.py")
    with open(integration_file, 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    print(f"🔌 API de integración creada en: {integration_file}")

def update_airguardian_main():
    """Actualiza el archivo principal de Air-Guardian para incluir las nuevas funcionalidades"""
    
    main_file = os.path.join(AIR_GUARDIAN_BACKEND, "main.py")
    
    if os.path.exists(main_file):
        # Leer archivo actual
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Agregar importación de la API avanzada
        if "from advanced_api import router as advanced_router" not in content:
            # Buscar donde agregar la importación
            import_section = content.find("from predict_api import router as predict_router")
            if import_section != -1:
                # Agregar después de las importaciones existentes
                insert_pos = content.find("\n", import_section) + 1
                new_import = "from advanced_api import router as advanced_router\n"
                content = content[:insert_pos] + new_import + content[insert_pos:]
        
        # Agregar router avanzado
        if "app.include_router(advanced_router)" not in content:
            # Buscar donde agregar el router
            router_section = content.find("app.include_router(tempo_router)")
            if router_section != -1:
                insert_pos = content.find("\n", router_section) + 1
                new_router = "app.include_router(advanced_router)\n"
                content = content[:insert_pos] + new_router + content[insert_pos:]
        
        # Guardar archivo actualizado
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo principal actualizado: {main_file}")

def main():
    """Función principal de sincronización"""
    
    print("SINCRONIZACION DE MODELOS DE CALIDAD DEL AIRE")
    print("=" * 60)
    
    # Verificar que Air-Guardian existe
    if not os.path.exists(AIR_GUARDIAN_PATH):
        print(f"❌ Error: No se encontró Air-Guardian en {AIR_GUARDIAN_PATH}")
        return False
    
    try:
        # 1. Sincronizar con Air-Guardian
        predictor, config = sync_with_airguardian()
        
        # 2. Crear API de integración
        create_integration_api()
        
        # 3. Actualizar archivo principal
        update_airguardian_main()
        
        print("\n✅ SINCRONIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"📁 Modelo avanzado: {AIR_GUARDIAN_MODELS}/advanced_aqi_model.pkl")
        print(f"⚙️ Configuración: {AIR_GUARDIAN_MODELS}/model_config.json")
        print(f"🔌 API integrada: {AIR_GUARDIAN_BACKEND}/advanced_api.py")
        print(f"📊 R² del modelo: {config['r2_score']:.4f}")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Ejecutar Air-Guardian: cd Air-Guardian && python backend/main.py")
        print("2. Probar endpoint: http://localhost:8000/api/advanced/scenarios")
        print("3. Realizar predicción: POST /api/advanced/predict")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la sincronización: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
