import os
from dotenv import load_dotenv

load_dotenv()

# OpenAQ API Configuration
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "a4b24931a824d4bb597b3da8a0ef2556328a454589dc44acfbed807090288e12")

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# OpenWeather API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_openweather_api_key_here")
