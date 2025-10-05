import React, { useState, useEffect } from 'react'
import { X, TrendingUp, Wind, Droplets, Thermometer, Gauge, Calendar } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { format, parseISO } from 'date-fns'
import { getAQIColor, getAQICategory, getAQIDescription } from '../utils/aqi'
import { fetchStationHistory, fetchWeather, fetchForecast } from '../services/api'
import './DetailPanel.css'

const DetailPanel = ({ station, onClose }) => {
  const [activeTab, setActiveTab] = useState('current')
  const [historyData, setHistoryData] = useState(null)
  const [weatherData, setWeatherData] = useState(null)
  const [forecastData, setForecastData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [historyPeriod, setHistoryPeriod] = useState(1) // days

  useEffect(() => {
    if (station) {
      loadData()
    }
  }, [station, historyPeriod])

  const loadData = async () => {
    setLoading(true)
    try {
      const [history, weather, forecast] = await Promise.all([
        fetchStationHistory(station.station_id, historyPeriod),
        fetchWeather(station.latitude, station.longitude),
        fetchForecast(station.station_id, 48)
      ])
      
      setHistoryData(history)
      setWeatherData(weather)
      setForecastData(forecast)
    } catch (error) {
      console.error('Error loading detail data:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderCurrentTab = () => (
    <div className="tab-content">
      <div className="aqi-display">
        <div className="aqi-main">
          <div 
            className="aqi-value-large"
            style={{ color: getAQIColor(station.aqi) }}
          >
            {station.aqi || 'N/A'}
          </div>
          <div className="aqi-category-large">
            {getAQICategory(station.aqi)}
          </div>
        </div>
        <p className="aqi-description">
          {getAQIDescription(station.aqi)}
        </p>
      </div>

      <div className="pollutants-grid">
        <h3>Pollutant Concentrations</h3>
        {station.pollutants && Object.entries(station.pollutants).map(([key, value]) => (
          <div key={key} className="pollutant-card">
            <div className="pollutant-card-header">
              <span className="pollutant-key">{key.toUpperCase()}</span>
              <span className="pollutant-unit">µg/m³</span>
            </div>
            <div className="pollutant-value-large">{value.toFixed(2)}</div>
            <div className="pollutant-bar">
              <div 
                className="pollutant-bar-fill"
                style={{ 
                  width: `${Math.min((value / 100) * 100, 100)}%`,
                  backgroundColor: getAQIColor(station.aqi)
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {weatherData && (
        <div className="weather-section">
          <h3>Weather Conditions</h3>
          <div className="weather-grid">
            <div className="weather-item">
              <Thermometer size={20} />
              <span className="weather-label">Temperature</span>
              <span className="weather-value">{weatherData.temperature.toFixed(1)}°C</span>
            </div>
            <div className="weather-item">
              <Droplets size={20} />
              <span className="weather-label">Humidity</span>
              <span className="weather-value">{weatherData.humidity.toFixed(0)}%</span>
            </div>
            <div className="weather-item">
              <Wind size={20} />
              <span className="weather-label">Wind Speed</span>
              <span className="weather-value">{weatherData.wind_speed.toFixed(1)} m/s</span>
            </div>
            <div className="weather-item">
              <Gauge size={20} />
              <span className="weather-label">Pressure</span>
              <span className="weather-value">{weatherData.pressure.toFixed(0)} hPa</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )

  const renderHistoryTab = () => {
    if (loading) {
      return <div className="loading-section">Loading historical data...</div>
    }

    if (!historyData || !historyData.data) {
      return <div className="no-data-section">No historical data available</div>
    }

    const chartData = historyData.data.map(item => ({
      time: format(parseISO(item.timestamp), 'MMM dd HH:mm'),
      aqi: item.aqi,
      pm25: item.pm25,
      pm10: item.pm10,
      no2: item.no2,
      o3: item.o3,
    }))

    // Sample data for better visualization
    const sampledData = chartData.filter((_, index) => {
      const totalPoints = chartData.length
      if (totalPoints <= 50) return true
      const step = Math.ceil(totalPoints / 50)
      return index % step === 0
    })

    return (
      <div className="tab-content">
        <div className="period-selector">
          <button 
            className={historyPeriod === 1 ? 'active' : ''}
            onClick={() => setHistoryPeriod(1)}
          >
            24h
          </button>
          <button 
            className={historyPeriod === 7 ? 'active' : ''}
            onClick={() => setHistoryPeriod(7)}
          >
            7 days
          </button>
          <button 
            className={historyPeriod === 30 ? 'active' : ''}
            onClick={() => setHistoryPeriod(30)}
          >
            30 days
          </button>
        </div>

        <div className="chart-container">
          <h3>Air Quality Index History</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={sampledData}>
              <defs>
                <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#63b3ed" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#63b3ed" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis 
                dataKey="time" 
                stroke="#a0aec0"
                tick={{ fontSize: 11 }}
                interval="preserveStartEnd"
              />
              <YAxis stroke="#a0aec0" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1f2e', 
                  border: '1px solid #2d3748',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#e6e9ef' }}
              />
              <Area 
                type="monotone" 
                dataKey="aqi" 
                stroke="#63b3ed" 
                fillOpacity={1} 
                fill="url(#colorAqi)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Pollutant Levels</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={sampledData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis 
                dataKey="time" 
                stroke="#a0aec0"
                tick={{ fontSize: 11 }}
                interval="preserveStartEnd"
              />
              <YAxis stroke="#a0aec0" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1f2e', 
                  border: '1px solid #2d3748',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#e6e9ef' }}
              />
              <Legend wrapperStyle={{ color: '#e6e9ef' }} />
              <Line type="monotone" dataKey="pm25" stroke="#f687b3" name="PM2.5" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="pm10" stroke="#fbb6ce" name="PM10" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="no2" stroke="#fc8181" name="NO₂" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="o3" stroke="#90cdf4" name="O₃" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  const renderForecastTab = () => {
    if (loading) {
      return <div className="loading-section">Loading forecast...</div>
    }

    if (!forecastData || !forecastData.forecast) {
      return <div className="no-data-section">No forecast data available</div>
    }

    const chartData = forecastData.forecast.map(item => ({
      time: format(parseISO(item.timestamp), 'MMM dd HH:mm'),
      aqi: item.aqi,
      confidence: (item.confidence || 0.8) * 100,
    }))

    // Sample data for 24 and 48 hour views
    const sampledData = chartData.filter((_, index) => index % 2 === 0)

    return (
      <div className="tab-content">
        <div className="forecast-header">
          <TrendingUp size={24} />
          <div>
            <h3>Air Quality Forecast</h3>
            <p>Predicted AQI for the next 48 hours</p>
          </div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={sampledData}>
              <defs>
                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#48bb78" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#48bb78" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis 
                dataKey="time" 
                stroke="#a0aec0"
                tick={{ fontSize: 11 }}
                interval="preserveStartEnd"
              />
              <YAxis stroke="#a0aec0" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1f2e', 
                  border: '1px solid #2d3748',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#e6e9ef' }}
                formatter={(value, name) => {
                  if (name === 'confidence') return `${value.toFixed(0)}%`
                  return value
                }}
              />
              <Legend wrapperStyle={{ color: '#e6e9ef' }} />
              <Area 
                type="monotone" 
                dataKey="aqi" 
                stroke="#48bb78" 
                fillOpacity={1} 
                fill="url(#colorForecast)"
                name="Predicted AQI"
              />
              <Line 
                type="monotone" 
                dataKey="confidence" 
                stroke="#ed8936" 
                strokeWidth={2}
                dot={false}
                name="Confidence"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="forecast-summary">
          <div className="forecast-card">
            <Calendar size={20} />
            <span className="forecast-label">12 Hours</span>
            <span 
              className="forecast-value"
              style={{ color: getAQIColor(chartData[5]?.aqi) }}
            >
              {chartData[5]?.aqi || 'N/A'}
            </span>
            <span className="forecast-category">
              {getAQICategory(chartData[5]?.aqi)}
            </span>
          </div>
          <div className="forecast-card">
            <Calendar size={20} />
            <span className="forecast-label">24 Hours</span>
            <span 
              className="forecast-value"
              style={{ color: getAQIColor(chartData[11]?.aqi) }}
            >
              {chartData[11]?.aqi || 'N/A'}
            </span>
            <span className="forecast-category">
              {getAQICategory(chartData[11]?.aqi)}
            </span>
          </div>
          <div className="forecast-card">
            <Calendar size={20} />
            <span className="forecast-label">48 Hours</span>
            <span 
              className="forecast-value"
              style={{ color: getAQIColor(chartData[23]?.aqi) }}
            >
              {chartData[23]?.aqi || 'N/A'}
            </span>
            <span className="forecast-category">
              {getAQICategory(chartData[23]?.aqi)}
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <div>
          <h2>{station.name}</h2>
          <p className="station-coords">
            {station.latitude.toFixed(4)}, {station.longitude.toFixed(4)}
          </p>
        </div>
        <button className="close-button" onClick={onClose}>
          <X size={24} />
        </button>
      </div>

      <div className="detail-tabs">
        <button 
          className={`tab-button ${activeTab === 'current' ? 'active' : ''}`}
          onClick={() => setActiveTab('current')}
        >
          Current
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
        <button 
          className={`tab-button ${activeTab === 'forecast' ? 'active' : ''}`}
          onClick={() => setActiveTab('forecast')}
        >
          Forecast
        </button>
      </div>

      <div className="detail-body">
        {activeTab === 'current' && renderCurrentTab()}
        {activeTab === 'history' && renderHistoryTab()}
        {activeTab === 'forecast' && renderForecastTab()}
      </div>
    </div>
  )
}

export default DetailPanel

