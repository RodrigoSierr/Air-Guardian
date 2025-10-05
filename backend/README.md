# AirGuardian Backend

FastAPI backend for AirGuardian air quality monitoring and prediction system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Update API keys in `.env`:
- `OPENWEATHER_API_KEY`: Get from https://openweathermap.org/api
- `NASA_API_KEY`: Get from https://api.nasa.gov/
- `OPENAQ_API_KEY`: Optional, OpenAQ v2 API is open

## Running the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### GET /api/stations
Get list of air quality monitoring stations
- Query params: `lat`, `lon`, `radius` (km)

### GET /api/station/{station_id}
Get detailed information for a specific station

### GET /api/weather
Get weather data for coordinates
- Query params: `lat`, `lon`

### GET /api/history/{station_id}
Get historical data for a station
- Query params: `days` (default: 7)

### GET /api/predict/{station_id}
Get air quality predictions for a station
- Query params: `hours` (default: 48, max: 48)

## Machine Learning Model

The prediction model is automatically trained on first run using synthetic data. To manually train:

```bash
python ml_model.py
```

The trained model is saved in `model/` directory.

