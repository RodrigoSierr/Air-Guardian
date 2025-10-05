"""
API endpoints for prediction layer functionality
Integrates with AirGuardian's existing system
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

router = APIRouter()

# Models for prediction layer
class PredictionData(BaseModel):
    station_id: str
    latitude: float
    longitude: float
    pm25: float
    pm10: float
    no2: float
    o3: float
    so2: float
    timestamp: str
    confidence: Optional[float] = None

class HeatmapData(BaseModel):
    latitude: float
    longitude: float
    value: float
    pollutant: str

class PredictionLayerResponse(BaseModel):
    station_id: str
    station_name: str
    predictions: List[PredictionData]
    heatmap_data: List[HeatmapData]
    scenarios: Dict[str, Any]

class AnalysisRequest(BaseModel):
    station_id: str
    analysis_type: str  # 'timeline', 'impact', 'interactive_timeline'

class AnalysisResponse(BaseModel):
    station_id: str
    analysis_type: str
    data: Dict[str, Any]
    charts: Dict[str, Any]

# Mock data generator for predictions
def generate_prediction_data(station_id: str, latitude: float, longitude: float, station_name: str) -> Dict[str, Any]:
    """Generate mock prediction data for a station"""
    
    # Base values for different pollutants
    base_values = {
        'pm25': np.random.uniform(10, 50),
        'pm10': np.random.uniform(20, 80),
        'no2': np.random.uniform(0.01, 0.05),
        'o3': np.random.uniform(0.02, 0.08),
        'so2': np.random.uniform(0.001, 0.01)
    }
    
    # Generate predictions for next 48 hours
    predictions = []
    current_time = datetime.now()
    
    for i in range(48):
        timestamp = current_time + timedelta(hours=i)
        
        # Add some variation to predictions
        variation = np.random.uniform(0.8, 1.2)
        
        prediction = PredictionData(
            station_id=station_id,
            latitude=latitude,
            longitude=longitude,
            pm25=max(0, base_values['pm25'] * variation),
            pm10=max(0, base_values['pm10'] * variation),
            no2=max(0, base_values['no2'] * variation),
            o3=max(0, base_values['o3'] * variation),
            so2=max(0, base_values['so2'] * variation),
            timestamp=timestamp.isoformat(),
            confidence=np.random.uniform(0.7, 0.95)
        )
        predictions.append(prediction)
    
    # Generate heatmap data
    heatmap_data = []
    pollutants = ['pm25', 'pm10', 'no2', 'o3', 'so2']
    
    for pollutant in pollutants:
        # Create a grid of points around the station
        for lat_offset in [-0.01, 0, 0.01]:
            for lon_offset in [-0.01, 0, 0.01]:
                heatmap_data.append(HeatmapData(
                    latitude=latitude + lat_offset,
                    longitude=longitude + lon_offset,
                    value=base_values[pollutant] * np.random.uniform(0.8, 1.2),
                    pollutant=pollutant
                ))
    
    # Generate scenarios
    scenarios = {
        'current': {
            'name': 'Current Trend',
            'description': 'Based on current conditions',
            'factor': 1.0
        },
        'green_policy': {
            'name': 'Green Policy',
            'description': 'Implementation of environmental policies',
            'factor': 0.7
        },
        'urban_growth': {
            'name': 'Urban Growth',
            'description': 'Increased urbanization and traffic',
            'factor': 1.3
        },
        'climate_emergency': {
            'name': 'Climate Emergency',
            'description': 'Drastic climate action measures',
            'factor': 0.5
        }
    }
    
    return {
        'station_id': station_id,
        'station_name': station_name,
        'predictions': predictions,
        'heatmap_data': heatmap_data,
        'scenarios': scenarios
    }

@router.get("/api/prediction-layer/{station_id}", response_model=PredictionLayerResponse)
async def get_prediction_layer(station_id: str):
    """Get prediction layer data for a specific station"""
    try:
        # Import here to avoid circular imports
        from main import get_stations
        
        # Get station data
        stations = await get_stations()
        station = next((s for s in stations if s.station_id == station_id), None)
        
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Generate prediction data
        prediction_data = generate_prediction_data(
            station_id, 
            station.latitude, 
            station.longitude, 
            station.name
        )
        
        return PredictionLayerResponse(**prediction_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating prediction layer: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

@router.get("/api/prediction-layer/heatmap/{pollutant}")
async def get_heatmap_data(pollutant: str, lat: Optional[float] = None, lon: Optional[float] = None, radius: float = 0.1):
    """Get heatmap data for a specific pollutant"""
    try:
        # If no coordinates provided, use default area
        if lat is None or lon is None:
            lat, lon = -12.0464, -77.0428  # Lima, Peru default
        
        # Generate heatmap data in a grid around the coordinates
        heatmap_data = []
        
        # Create a grid of points
        for lat_offset in np.arange(-radius, radius + 0.01, 0.01):
            for lon_offset in np.arange(-radius, radius + 0.01, 0.01):
                # Generate random values based on pollutant
                if pollutant == 'pm25':
                    value = np.random.uniform(10, 60)
                elif pollutant == 'pm10':
                    value = np.random.uniform(20, 100)
                elif pollutant == 'no2':
                    value = np.random.uniform(0.01, 0.05)
                elif pollutant == 'o3':
                    value = np.random.uniform(0.02, 0.08)
                elif pollutant == 'so2':
                    value = np.random.uniform(0.001, 0.01)
                else:
                    value = np.random.uniform(10, 50)
                
                heatmap_data.append({
                    'latitude': lat + lat_offset,
                    'longitude': lon + lon_offset,
                    'value': value,
                    'pollutant': pollutant
                })
        
        return {
            'pollutant': pollutant,
            'data': heatmap_data,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating heatmap data: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating heatmap: {str(e)}")

@router.post("/api/prediction-layer/analysis", response_model=AnalysisResponse)
async def get_analysis(request: AnalysisRequest):
    """Get analysis data for a specific station and analysis type"""
    try:
        # Import here to avoid circular imports
        from main import get_stations
        
        # Get station data
        stations = await get_stations()
        station = next((s for s in stations if s.station_id == request.station_id), None)
        
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Generate analysis data based on type
        if request.analysis_type == 'timeline':
            analysis_data = generate_timeline_analysis(station)
        elif request.analysis_type == 'impact':
            analysis_data = generate_impact_analysis(station)
        elif request.analysis_type == 'interactive_timeline':
            analysis_data = generate_interactive_timeline_analysis(station)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        return AnalysisResponse(
            station_id=request.station_id,
            analysis_type=request.analysis_type,
            data=analysis_data['data'],
            charts=analysis_data['charts']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

def generate_timeline_analysis(station) -> Dict[str, Any]:
    """Generate timeline analysis data"""
    # Generate historical data (last 30 days)
    historical_data = []
    current_time = datetime.now()
    
    for i in range(30):
        date = current_time - timedelta(days=30-i)
        historical_data.append({
            'date': date.isoformat(),
            'pm25': np.random.uniform(10, 60),
            'pm10': np.random.uniform(20, 100),
            'no2': np.random.uniform(0.01, 0.05),
            'o3': np.random.uniform(0.02, 0.08)
        })
    
    # Generate future predictions
    future_data = []
    for i in range(48):
        date = current_time + timedelta(hours=i)
        future_data.append({
            'date': date.isoformat(),
            'pm25': np.random.uniform(15, 70),
            'pm10': np.random.uniform(25, 110),
            'no2': np.random.uniform(0.015, 0.06),
            'o3': np.random.uniform(0.025, 0.09)
        })
    
    return {
        'data': {
            'historical': historical_data,
            'future': future_data,
            'station_name': station.name
        },
        'charts': {
            'type': 'timeline',
            'title': f'Timeline Analysis - {station.name}',
            'description': 'Historical and future air quality trends'
        }
    }

def generate_impact_analysis(station) -> Dict[str, Any]:
    """Generate impact analysis data"""
    # Generate comparison data between historical and predicted
    pollutants = ['pm25', 'pm10', 'no2', 'o3']
    
    comparison_data = {}
    for pollutant in pollutants:
        historical_avg = np.random.uniform(10, 50)
        predicted_avg = historical_avg * np.random.uniform(0.8, 1.3)
        
        comparison_data[pollutant] = {
            'historical': historical_avg,
            'predicted': predicted_avg,
            'change_percent': ((predicted_avg - historical_avg) / historical_avg) * 100
        }
    
    return {
        'data': {
            'comparison': comparison_data,
            'station_name': station.name,
            'analysis_date': datetime.now().isoformat()
        },
        'charts': {
            'type': 'impact',
            'title': f'Impact Analysis - {station.name}',
            'description': 'Comparison between historical and predicted values'
        }
    }

def generate_interactive_timeline_analysis(station) -> Dict[str, Any]:
    """Generate interactive timeline analysis data"""
    # Generate scenarios data
    scenarios = ['current', 'green_policy', 'urban_growth', 'climate_emergency']
    scenario_data = {}
    
    for scenario in scenarios:
        scenario_data[scenario] = []
        for i in range(24):  # 24 hours ahead
            date = datetime.now() + timedelta(hours=i)
            
            # Different factors for different scenarios
            if scenario == 'current':
                factor = 1.0
            elif scenario == 'green_policy':
                factor = 0.7
            elif scenario == 'urban_growth':
                factor = 1.3
            elif scenario == 'climate_emergency':
                factor = 0.5
            
            scenario_data[scenario].append({
                'date': date.isoformat(),
                'pm25': np.random.uniform(10, 50) * factor,
                'pm10': np.random.uniform(20, 80) * factor,
                'no2': np.random.uniform(0.01, 0.05) * factor,
                'o3': np.random.uniform(0.02, 0.08) * factor
            })
    
    return {
        'data': {
            'scenarios': scenario_data,
            'station_name': station.name,
            'generated_at': datetime.now().isoformat()
        },
        'charts': {
            'type': 'interactive_timeline',
            'title': f'Interactive Timeline - {station.name}',
            'description': 'Multiple scenarios for future air quality'
        }
    }

@router.get("/api/prediction-layer/toggle")
async def toggle_prediction_layer(enabled: bool = True):
    """Toggle prediction layer visibility"""
    return {
        'enabled': enabled,
        'message': f'Prediction layer {"enabled" if enabled else "disabled"}',
        'timestamp': datetime.now().isoformat()
    }
