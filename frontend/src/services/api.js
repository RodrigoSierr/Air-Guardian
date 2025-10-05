import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export const fetchStations = async (lat = null, lon = null, radius = 50) => {
  try {
    const params = {}
    if (lat && lon) {
      params.lat = lat
      params.lon = lon
      params.radius = radius
    }
    
    const response = await api.get('/api/stations', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching stations:', error)
    // Return empty array instead of throwing to prevent app crash
    return []
  }
}

export const fetchStationsByCountry = async (country = 'PE', limit = 100) => {
  try {
    const response = await api.get(`/api/stations/by-country/${country}`, {
      params: { limit }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching stations by country:', error)
    return []
  }
}

export const fetchStationDetails = async (stationId) => {
  try {
    const response = await api.get(`/api/station/${stationId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching station details:', error)
    throw error
  }
}

export const fetchStationHistory = async (stationId, days = 7) => {
  try {
    const response = await api.get(`/api/history/${stationId}`, {
      params: { days }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching station history:', error)
    throw error
  }
}

export const fetchWeather = async (lat, lon) => {
  try {
    const response = await api.get('/api/weather', {
      params: { lat, lon }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching weather:', error)
    throw error
  }
}

export const fetchForecast = async (stationId, hours = 48) => {
  try {
    const response = await api.get(`/api/predict/${stationId}`, {
      params: { hours }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching forecast:', error)
    throw error
  }
}

export const fetchAdvancedForecast = async (stationId, currentData, hours = 48, scenario = 'tendencia_actual') => {
  try {
    const response = await api.post('/api/advanced/predict', {
      station_id: stationId,
      current_data: currentData,
      hours_ahead: hours,
      scenario: scenario
    })
    return response.data
  } catch (error) {
    console.error('Error fetching advanced forecast:', error)
    throw error
  }
}

export const sendNotification = async (userData) => {
  try {
    const response = await api.post('/api/send-notification', userData)
    return response.data
  } catch (error) {
    console.error('Error sending notification:', error)
    throw error
  }
}

export default api

