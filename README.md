# AirGuardian 🌍💨

Una aplicación web completa para el pronóstico de calidad del aire que integra datos en tiempo real de satélites, sensores terrestres y datos meteorológicos con machine learning para predicciones precisas.

Video Introductorio + Responsables del desarrollo: https://www.youtube.com/watch?v=40QMoU_xU5c

![AirGuardian](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)

## 🌟 Características

- **Mapa Interactivo**: Visualización de estaciones de monitoreo en tiempo real con Leaflet
- **Datos en Tiempo Real**: Integración con OpenAQ, NASA TEMPO y OpenWeatherMap
- **Predicciones ML**: Modelo de machine learning para pronosticar la calidad del aire (12-48 horas)
- **Tema Oscuro**: Interfaz moderna inspirada en qairamap.qairadrones.com
- **Análisis Histórico**: Gráficos de tendencias de contaminantes
- **Responsive**: Funciona en dispositivos móviles y escritorio

## 🏗️ Arquitectura

```
airguardian/
├── backend/              # FastAPI backend
│   ├── main.py          # API principal
│   ├── ml_model.py      # Modelo de predicción
│   ├── predict_api.py   # Endpoints de predicción
│   └── requirements.txt # Dependencias Python
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── services/    # Servicios API
│   │   └── utils/       # Utilidades
│   └── package.json     # Dependencias Node
│
└── README.md
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.9+
- Node.js 18+
- npm o yarn

### Backend Setup

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (opcional)
# Añade tus API keys aquí
OPENWEATHER_API_KEY=tu_api_key
NASA_API_KEY=DEMO_KEY

# Iniciar servidor
python main.py
```

El backend estará disponible en `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📡 APIs Utilizadas

### OpenAQ (Datos Terrestres)
- **URL**: https://api.openaq.org/v2/
- **Datos**: PM2.5, PM10, NO₂, O₃, CO, SO₂
- **Cobertura**: Global
- **API Key**: No requerida para uso básico

### OpenWeatherMap (Datos Meteorológicos)
- **URL**: https://api.openweathermap.org/data/2.5/
- **Datos**: Temperatura, humedad, viento, presión
- **API Key**: Requerida (gratis hasta 1000 llamadas/día)
- **Registro**: https://openweathermap.org/api

### NASA TEMPO (Datos Satelitales)
- **URL**: https://api.nasa.gov/
- **Datos**: NO₂, O₃ desde satélite
- **API Key**: Usa "DEMO_KEY" o registra en https://api.nasa.gov/
- **Nota**: Implementación básica incluida, expandible

## 🤖 Modelo de Machine Learning

El sistema incluye un modelo predictivo basado en Random Forest que:

- **Predice**: AQI para las próximas 12, 24 y 48 horas
- **Features**: 
  - Datos históricos de contaminantes (PM2.5, PM10, NO₂, O₃)
  - Datos meteorológicos (temperatura, humedad, viento, presión)
  - Características temporales (hora, día de semana, mes)
  - Features de lag (valores anteriores)
  - Estadísticas rolling (medias móviles)

### Entrenamiento del Modelo

```bash
cd backend
python ml_model.py
```

El modelo se entrena automáticamente con datos sintéticos en el primer inicio. Para usar datos reales:

1. Recopila datos históricos de OpenAQ
2. Modifica `ml_model.py` para usar tus datos
3. Re-entrena el modelo

## 🎨 Interfaz de Usuario

### Componentes Principales

1. **Header**: Logo, título y información de actualización
2. **Sidebar**: Lista de estaciones con filtros y búsqueda
3. **MapView**: Mapa interactivo con marcadores de estaciones
4. **DetailPanel**: Detalles, gráficos históricos y pronósticos

### Paleta de Colores (AQI)

- 🟢 **Verde** (0-50): Buena
- 🟡 **Amarillo** (51-100): Moderada
- 🟠 **Naranja** (101-150): Insalubre para grupos sensibles
- 🔴 **Rojo** (151-200): Insalubre
- 🟣 **Morado** (201-300): Muy insalubre
- 🟤 **Marrón** (301+): Peligrosa

## 🔧 Desarrollo

### Estructura de Componentes React

```jsx
App
├── Header
├── Sidebar
│   └── StationCard (lista)
├── MapView
│   ├── TileLayer (CartoDB Dark)
│   └── CircleMarker (estaciones)
└── DetailPanel
    ├── CurrentTab
    ├── HistoryTab (gráficos)
    └── ForecastTab (predicciones)
```

### API Endpoints

#### GET `/api/stations`
Obtiene lista de estaciones de monitoreo
```
Query params: lat, lon, radius
Response: Array<StationData>
```

#### GET `/api/station/{station_id}`
Detalles de una estación específica

#### GET `/api/weather`
Datos meteorológicos para coordenadas
```
Query params: lat, lon
Response: WeatherData
```

#### GET `/api/history/{station_id}`
Datos históricos de una estación
```
Query params: days (default: 7)
Response: { station_id, data: Array }
```

#### GET `/api/predict/{station_id}`
Pronóstico de AQI
```
Query params: hours (default: 48, max: 48)
Response: ForecastResponse
```

## 📊 Visualizaciones

La aplicación usa **Recharts** para gráficos:

- **AreaChart**: Tendencias de AQI
- **LineChart**: Niveles de contaminantes múltiples
- **Gráficos responsivos**: Se adaptan al tamaño de pantalla

## 🌐 Despliegue

### Docker (Recomendado)

```bash
# Construir y ejecutar con Docker Compose
docker-compose up -d
```

### Vercel (Frontend)

```bash
cd frontend
npm run build
vercel --prod
```

### Railway/Heroku (Backend)

```bash
cd backend
# Crear Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
# Deploy según la plataforma
```

## 🔐 Variables de Entorno

### Backend (.env)
```
OPENAQ_API_KEY=optional
OPENWEATHER_API_KEY=your_key
NASA_API_KEY=DEMO_KEY
CORS_ORIGINS=http://localhost:5173,https://tu-dominio.com
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Roadmap

- [x] Integración de datos en tiempo real
- [x] Modelo predictivo básico
- [x] Interfaz de usuario completa
- [ ] Capa completa de datos TEMPO (heatmap)
- [ ] Sistema de autenticación de usuarios
- [ ] Alertas personalizadas por email/push
- [ ] Aplicación móvil (React Native)
- [ ] Modelo LSTM para mejores predicciones
- [ ] API de alertas automáticas
- [ ] Dashboard administrativo

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado como proyecto educacional de geo-visualización y machine learning.

## 🙏 Agradecimientos

- [OpenAQ](https://openaq.org/) - Datos de calidad del aire
- [OpenWeatherMap](https://openweathermap.org/) - Datos meteorológicos
- [NASA](https://www.nasa.gov/) - Datos satelitales TEMPO
- [qairamap.qairadrones.com](https://qairamap.qairadrones.com/) - Inspiración de diseño
- [Leaflet](https://leafletjs.com/) - Mapas interactivos
- [FastAPI](https://fastapi.tiangolo.com/) - Framework backend
- [React](https://react.dev/) - Framework frontend

## 📞 Soporte

Para preguntas o soporte, abre un issue en el repositorio.

---

Hecho con ❤️ y ☕ para un aire más limpio

