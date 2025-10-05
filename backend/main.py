from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio

load_dotenv()

app = FastAPI(title="AirGuardian API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class StationData(BaseModel):
    station_id: str
    name: str
    latitude: float
    longitude: float
    aqi: Optional[int] = None
    pollutants: dict
    last_update: str

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

class WeatherData(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: int
    pressure: float

# Helper functions
def calculate_aqi_pm25(pm25: float) -> int:
    """Calculate AQI from PM2.5 concentration (µg/m³)"""
    if pm25 <= 12.0:
        return int((50 / 12.0) * pm25)
    elif pm25 <= 35.4:
        return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
    elif pm25 <= 55.4:
        return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
    elif pm25 <= 150.4:
        return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5))
    elif pm25 <= 250.4:
        return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5))
    else:
        return int(300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5))

def get_aqi_color(aqi: int) -> str:
    """Get color based on AQI value"""
    if aqi <= 50:
        return "#00E400"  # Green
    elif aqi <= 100:
        return "#FFFF00"  # Yellow
    elif aqi <= 150:
        return "#FF7E00"  # Orange
    elif aqi <= 200:
        return "#FF0000"  # Red
    elif aqi <= 300:
        return "#8F3F97"  # Purple
    else:
        return "#7E0023"  # Maroon

# API Endpoints
@app.get("/")
async def root():
    return {"message": "AirGuardian API", "version": "1.0.0"}

@app.get("/api/stations", response_model=List[StationData])
async def get_stations(lat: Optional[float] = None, lon: Optional[float] = None, radius: int = 50):
    """Get air quality monitoring stations from OpenAQ"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # OpenAQ API v2
            params = {
                "limit": 100,
                "order_by": "lastUpdated",
                "sort": "desc"
            }
            
            if lat and lon:
                params["coordinates"] = f"{lat},{lon}"
                params["radius"] = radius * 1000  # Convert km to meters
            
            response = await client.get(
                "https://api.openaq.org/v2/latest",
                params=params
            )
            
            if response.status_code != 200:
                # Return mock data if API fails
                return get_mock_stations()
            
            data = response.json()
            stations = []
            
            for result in data.get("results", [])[:50]:  # Limit to 50 stations
                measurements = result.get("measurements", [])
                pollutants = {}
                pm25_value = None
                
                for measurement in measurements:
                    parameter = measurement.get("parameter")
                    value = measurement.get("value")
                    if parameter and value:
                        pollutants[parameter] = value
                        if parameter == "pm25":
                            pm25_value = value
                
                # Calculate AQI from PM2.5 if available
                aqi = calculate_aqi_pm25(pm25_value) if pm25_value else None
                
                coordinates = result.get("coordinates", {})
                location = result.get("location", "Unknown")
                
                if coordinates.get("latitude") and coordinates.get("longitude"):
                    station = StationData(
                        station_id=str(result.get("location", "").replace(" ", "_") + "_" + str(result.get("locationId", ""))),
                        name=location,
                        latitude=coordinates["latitude"],
                        longitude=coordinates["longitude"],
                        aqi=aqi,
                        pollutants=pollutants,
                        last_update=result.get("lastUpdated", datetime.utcnow().isoformat())
                    )
                    stations.append(station)
            
            return stations if stations else get_mock_stations()
            
    except Exception as e:
        print(f"Error fetching stations: {e}")
        # Return mock data on error
        return get_mock_stations()

def get_mock_stations() -> List[StationData]:
    """Return mock station data for development"""
    import random
    
    cities = [
        {"name": "Lima Centro", "lat": -12.0464, "lon": -77.0428},
        {"name": "Lima Norte", "lat": -11.9856, "lon": -77.0502},
        {"name": "Callao", "lat": -12.0565, "lon": -77.1181},
        {"name": "San Isidro", "lat": -12.0931, "lon": -77.0465},
        {"name": "Miraflores", "lat": -12.1196, "lon": -77.0288},
        {"name": "Santiago Centro", "lat": -33.4489, "lon": -70.6693},
        {"name": "Mexico City", "lat": 19.4326, "lon": -99.1332},
        {"name": "Bogotá", "lat": 4.7110, "lon": -74.0721},
    ]
    
    stations = []
    for i, city in enumerate(cities):
        pm25 = random.uniform(10, 180)
        aqi = calculate_aqi_pm25(pm25)
        
        station = StationData(
            station_id=f"station_{i+1}",
            name=city["name"],
            latitude=city["lat"] + random.uniform(-0.05, 0.05),
            longitude=city["lon"] + random.uniform(-0.05, 0.05),
            aqi=aqi,
            pollutants={
                "pm25": round(pm25, 2),
                "pm10": round(pm25 * 1.5, 2),
                "no2": round(random.uniform(10, 80), 2),
                "o3": round(random.uniform(20, 100), 2),
            },
            last_update=datetime.utcnow().isoformat()
        )
        stations.append(station)
    
    return stations

@app.get("/api/station/{station_id}")
async def get_station_details(station_id: str):
    """Get detailed information for a specific station"""
    stations = await get_stations()
    station = next((s for s in stations if s.station_id == station_id), None)
    
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return station

@app.get("/api/weather")
async def get_weather(lat: float, lon: float):
    """Get weather data from OpenWeatherMap"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key or api_key == "your_openweather_api_key_here":
        # Return mock weather data
        import random
        return WeatherData(
            temperature=random.uniform(15, 30),
            humidity=random.uniform(40, 80),
            wind_speed=random.uniform(2, 15),
            wind_direction=random.randint(0, 360),
            pressure=random.uniform(1010, 1020)
        )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": api_key,
                    "units": "metric"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return WeatherData(
                    temperature=data["main"]["temp"],
                    humidity=data["main"]["humidity"],
                    wind_speed=data["wind"]["speed"],
                    wind_direction=data["wind"]["deg"],
                    pressure=data["main"]["pressure"]
                )
    except Exception as e:
        print(f"Error fetching weather: {e}")
    
    raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@app.get("/api/history/{station_id}")
async def get_station_history(station_id: str, days: int = 7):
    """Get historical data for a station (mock data for now)"""
    import random
    from datetime import datetime, timedelta
    
    # Generate mock historical data
    history = []
    now = datetime.utcnow()
    
    # Generate data points every hour for the specified days
    for i in range(days * 24):
        timestamp = now - timedelta(hours=days * 24 - i)
        base_pm25 = 50 + 30 * (i / (days * 24))  # Gradual increase
        noise = random.uniform(-20, 20)
        pm25 = max(5, base_pm25 + noise)
        
        history.append({
            "timestamp": timestamp.isoformat(),
            "pm25": round(pm25, 2),
            "pm10": round(pm25 * 1.5, 2),
            "no2": round(random.uniform(20, 80), 2),
            "o3": round(random.uniform(30, 100), 2),
            "aqi": calculate_aqi_pm25(pm25)
        })
    
    return {"station_id": station_id, "data": history}

# Include prediction endpoints
from predict_api import router as predict_router
app.include_router(predict_router)

# Include TEMPO satellite data endpoints
from tempo_api import router as tempo_router
app.include_router(tempo_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

