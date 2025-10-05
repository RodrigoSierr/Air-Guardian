# AirGuardian Frontend

React + Vite frontend for AirGuardian air quality monitoring system.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional):
```bash
VITE_API_URL=http://localhost:8000
```

## Running the Development Server

```bash
npm run dev
```

The application will be available at http://localhost:5173

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Features

- **Interactive Map**: Leaflet-based map showing air quality monitoring stations
- **Real-time Data**: Live air quality data from OpenAQ and other sources
- **Dark Theme**: Beautiful dark theme inspired by qairamap.qairadrones.com
- **Station Details**: Detailed view with current conditions, historical data, and forecasts
- **Historical Charts**: Visualize air quality trends over time
- **AI Predictions**: Machine learning-powered air quality forecasts
- **Responsive Design**: Works on desktop and mobile devices

## Technologies

- React 18
- Vite
- Leaflet & React-Leaflet
- Recharts
- Axios
- date-fns
- Lucide React (icons)

