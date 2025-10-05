from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
from config import OPENAQ_API_KEY, CORS_ORIGINS, OPENWEATHER_API_KEY

load_dotenv()

app = FastAPI(title="AirGuardian API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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
            # OpenAQ API v3 with API key
            headers = {
                "X-API-Key": OPENAQ_API_KEY
            }
            
            params = {
                "limit": 100,
                "order_by": "lastUpdated",
                "sort": "desc"
            }
            
            if lat is not None and lon is not None:
                params["coordinates"] = f"{lat},{lon}"
                params["radius"] = radius * 1000  # Convert km to meters
            
            response = await client.get(
                "https://api.openaq.org/v3/latest",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"OpenAQ API error: {response.status_code} - {response.text}")
                # Try to get data from multiple countries as fallback
                return await get_fallback_stations()
            
            data = response.json()
            stations = []
            
            for result in data.get("results", [])[:50]:  # Limit to 50 stations
                measurements = result.get("measurements", [])
                pollutants = {}
                pm25_value = None
                pm10_value = None
                no2_value = None
                o3_value = None
                
                for measurement in measurements:
                    parameter = measurement.get("parameter")
                    value = measurement.get("value")
                    if parameter and value:
                        pollutants[parameter] = value
                        if parameter == "pm25":
                            pm25_value = value
                        elif parameter == "pm10":
                            pm10_value = value
                        elif parameter == "no2":
                            no2_value = value
                        elif parameter == "o3":
                            o3_value = value
                
                # Calculate AQI from PM2.5 if available, otherwise use PM10
                aqi = None
                if pm25_value:
                    aqi = calculate_aqi_pm25(pm25_value)
                elif pm10_value:
                    # Convert PM10 to PM2.5 equivalent (rough estimation)
                    pm25_equivalent = pm10_value * 0.7
                    aqi = calculate_aqi_pm25(pm25_equivalent)
                
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

async def get_fallback_stations() -> List[StationData]:
    """Try to get stations from multiple countries as fallback"""
    countries = ['US', 'MX', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'AU', 'JP']
    all_stations = []
    
    for country in countries[:3]:  # Try first 3 countries
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"X-API-Key": OPENAQ_API_KEY}
                params = {
                    "limit": 20,
                    "country": country,
                    "order_by": "lastUpdated",
                    "sort": "desc"
                }
                
                response = await client.get(
                    "https://api.openaq.org/v3/latest",
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for result in data.get("results", []):
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
                        
                        aqi = calculate_aqi_pm25(pm25_value) if pm25_value else None
                        coordinates = result.get("coordinates", {})
                        location = result.get("location", "Unknown")
                        
                        if coordinates.get("latitude") is not None and coordinates.get("longitude") is not None:
                            station = StationData(
                                station_id=str(result.get("location", "").replace(" ", "_") + "_" + str(result.get("locationId", ""))),
                                name=location,
                                latitude=coordinates["latitude"],
                                longitude=coordinates["longitude"],
                                aqi=aqi,
                                pollutants=pollutants,
                                last_update=result.get("lastUpdated", datetime.utcnow().isoformat())
                            )
                            all_stations.append(station)
                            
                            if len(all_stations) >= 30:  # Limit total stations
                                break
                                
        except Exception as e:
            print(f"Error fetching stations from {country}: {e}")
            continue
    
    # If we got some real data, return it, otherwise return mock data
    return all_stations if all_stations else get_mock_stations()

def get_mock_stations() -> List[StationData]:
    """Return mock station data for development"""
    import random
    
    cities = [
        # Perú - Lima y alrededores
        {"name": "Lima Centro", "lat": -12.0464, "lon": -77.0428},
        {"name": "Lima Norte", "lat": -11.9856, "lon": -77.0502},
        {"name": "Callao", "lat": -12.0565, "lon": -77.1181},
        {"name": "San Isidro", "lat": -12.0931, "lon": -77.0465},
        {"name": "Miraflores", "lat": -12.1196, "lon": -77.0288},
        {"name": "La Molina", "lat": -12.0708, "lon": -76.9656},
        {"name": "Surco", "lat": -12.1508, "lon": -76.9908},
        {"name": "Pueblo Libre", "lat": -12.0753, "lon": -77.0625},
        {"name": "Jesús María", "lat": -12.0833, "lon": -77.0333},
        {"name": "Magdalena", "lat": -12.0958, "lon": -77.0781},
        
        # Chile
        {"name": "Santiago Centro", "lat": -33.4489, "lon": -70.6693},
        {"name": "Valparaíso", "lat": -33.0472, "lon": -71.6127},
        {"name": "Concepción", "lat": -36.8201, "lon": -73.0444},
        {"name": "Antofagasta", "lat": -23.6509, "lon": -70.3975},
        
        # México
        {"name": "Mexico City Centro", "lat": 19.4326, "lon": -99.1332},
        {"name": "Guadalajara", "lat": 20.6597, "lon": -103.3496},
        {"name": "Monterrey", "lat": 25.6866, "lon": -100.3161},
        {"name": "Puebla", "lat": 19.0414, "lon": -98.2063},
        
        # Colombia
        {"name": "Bogotá Centro", "lat": 4.7110, "lon": -74.0721},
        {"name": "Medellín", "lat": 6.2442, "lon": -75.5812},
        {"name": "Cali", "lat": 3.4516, "lon": -76.5320},
        {"name": "Barranquilla", "lat": 10.9685, "lon": -74.7813},
        
        # Argentina
        {"name": "Buenos Aires", "lat": -34.6118, "lon": -58.3960},
        {"name": "Córdoba", "lat": -31.4201, "lon": -64.1888},
        {"name": "Rosario", "lat": -32.9442, "lon": -60.6505},
        
        # Brasil
        {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333},
        {"name": "Río de Janeiro", "lat": -22.9068, "lon": -43.1729},
        {"name": "Brasilia", "lat": -15.7801, "lon": -47.9292},
        
        # Ecuador
        {"name": "Quito", "lat": -0.1807, "lon": -78.4678},
        {"name": "Guayaquil", "lat": -2.1894, "lon": -79.8890},
        
        # Bolivia
        {"name": "La Paz", "lat": -16.2902, "lon": -68.1346},
        {"name": "Santa Cruz", "lat": -17.7833, "lon": -63.1833},
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

@app.get("/api/stations/by-country/{country}")
async def get_stations_by_country(country: str, limit: int = 100):
    """Get air quality stations for a specific country"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "X-API-Key": OPENAQ_API_KEY
            }
            
            # Use the latest measurements endpoint with country filter
            params = {
                "limit": limit,
                "country": country,
                "order_by": "lastUpdated",
                "sort": "desc"
            }
            
            response = await client.get(
                "https://api.openaq.org/v3/latest",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"OpenAQ API error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            stations = []
            
            for result in data.get("results", []):
                measurements = result.get("measurements", [])
                pollutants = {}
                pm25_value = None
                pm10_value = None
                
                for measurement in measurements:
                    parameter = measurement.get("parameter")
                    value = measurement.get("value")
                    if parameter and value:
                        pollutants[parameter] = value
                        if parameter == "pm25":
                            pm25_value = value
                        elif parameter == "pm10":
                            pm10_value = value
                
                # Calculate AQI from PM2.5 if available, otherwise use PM10
                aqi = None
                if pm25_value:
                    aqi = calculate_aqi_pm25(pm25_value)
                elif pm10_value:
                    # Convert PM10 to PM2.5 equivalent (rough estimation)
                    pm25_equivalent = pm10_value * 0.7
                    aqi = calculate_aqi_pm25(pm25_equivalent)
                
                coordinates = result.get("coordinates", {})
                location = result.get("location", "Unknown")
                
                if coordinates.get("latitude") is not None and coordinates.get("longitude") is not None:
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
            
            return stations
            
    except Exception as e:
        print(f"Error fetching stations by country: {e}")
        return []

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
    api_key = OPENWEATHER_API_KEY
    
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

