
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
import json

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
    print("Modelo avanzado cargado exitosamente")
else:
    advanced_predictor = None
    print("Modelo avanzado no encontrado")

@router.post("/predict", response_model=AdvancedPredictionResponse)
async def advanced_predict(request: AdvancedPredictionRequest):
    """Prediccion avanzada con multiples escenarios"""
    if advanced_predictor is None:
        raise HTTPException(status_code=503, detail="Modelo avanzado no disponible")
    
    try:
        # Realizar predicciones para multiples escenarios
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
                
                # Crear caracteristicas
                features = {
                    'hour_sin': np.sin(2 * np.pi * future_time.hour / 24),
                    'hour_cos': np.cos(2 * np.pi * future_time.hour / 24),
                    'month_sin': np.sin(2 * np.pi * future_time.month / 12),
                    'month_cos': np.cos(2 * np.pi * future_time.month / 12),
                    'is_weekend': 1 if future_time.weekday() >= 5 else 0,
                    **request.current_data
                }
                
                # Agregar caracteristicas de lag
                for col in model_config['outputs']:
                    features[f'{col}_lag_1h'] = request.current_data.get(col, 30)
                    features[f'{col}_lag_3h'] = request.current_data.get(col, 30)
                    features[f'{col}_lag_6h'] = request.current_data.get(col, 30)
                    features[f'{col}_lag_24h'] = request.current_data.get(col, 30)
                
                # Agregar estadisticas moviles
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
                    print(f"Error en prediccion: {e}")
                    continue
            
            predictions[scenario_name] = scenario_predictions
        
        return AdvancedPredictionResponse(
            station_id=request.station_id,
            predictions=predictions,
            model_info=model_config,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en prediccion: {str(e)}")

@router.get("/scenarios")
async def get_available_scenarios():
    """Obtiene escenarios disponibles para prediccion"""
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
    """Obtiene informacion del modelo avanzado"""
    if advanced_predictor is None:
        raise HTTPException(status_code=503, detail="Modelo avanzado no disponible")
    
    return model_config
