"""
Prediction API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ml_model import AirQualityPredictor
import asyncio

router = APIRouter()

# Define models locally to avoid circular imports
class ForecastPoint(BaseModel):
    timestamp: str
    aqi: int
    confidence: Optional[float] = None

class ForecastResponse(BaseModel):
    station_id: str
    station_name: str
    current_aqi: int
    forecast: List[ForecastPoint]
    generated_at: str

# Initialize predictor (load or train model)
predictor = AirQualityPredictor()
try:
    predictor.load_model()
except:
    print("Training new model...")
    predictor.train()

@router.get("/api/predict/{station_id}", response_model=ForecastResponse)
async def predict_air_quality(station_id: str, hours: int = 48):
    """
    Predict air quality for a specific station
    """
    try:
        # Import here to avoid circular imports
        from main import get_stations, get_weather
        
        # Get current station data
        stations = await get_stations()
        station = next((s for s in stations if s.station_id == station_id), None)
        
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Get weather data
        try:
            weather = await get_weather(station.latitude, station.longitude)
            weather_dict = weather.dict()
        except:
            weather_dict = {
                'temperature': 20,
                'humidity': 60,
                'wind_speed': 5,
                'pressure': 1013
            }
        
        # Prepare current data for prediction
        current_data = {
            'timestamp': station.last_update,
            'pm25': station.pollutants.get('pm25', 30),
            'pm10': station.pollutants.get('pm10', 45),
            'no2': station.pollutants.get('no2', 40),
            'o3': station.pollutants.get('o3', 50),
            'temperature': weather_dict['temperature'],
            'humidity': weather_dict['humidity'],
            'wind_speed': weather_dict['wind_speed'],
            'pressure': weather_dict['pressure'],
        }
        
        # Generate predictions
        predictions = predictor.predict_future(current_data, hours_ahead=min(hours, 48))
        
        # Convert to response format
        forecast_points = [
            ForecastPoint(
                timestamp=pred['timestamp'],
                aqi=pred['aqi'],
                confidence=pred.get('confidence')
            )
            for pred in predictions
        ]
        
        return ForecastResponse(
            station_id=station_id,
            station_name=station.name,
            current_aqi=station.aqi or 0,
            forecast=forecast_points,
            generated_at=current_data['timestamp']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

