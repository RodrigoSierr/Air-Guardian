import React, { useState, useEffect } from 'react'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import DetailPanel from './components/DetailPanel'
import Header from './components/Header'
import UserModal from './components/UserModal'
import { fetchStations, fetchStationsByCountry } from './services/api'
import './App.css'

function App() {
  const [stations, setStations] = useState([])
  const [selectedStation, setSelectedStation] = useState(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [userLocation, setUserLocation] = useState(null)

  useEffect(() => {
    loadStations()
  }, [])

  const loadStations = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Try to get stations by country first (Peru), then fallback to general stations
      let data = await fetchStationsByCountry('PE', 50)
      
      // If no data from Peru, try general stations
      if (!data || data.length === 0) {
        data = await fetchStations()
      }
      
      // If still no data, try other countries
      if (!data || data.length === 0) {
        data = await fetchStationsByCountry('US', 30)
      }
      
      if (!data || data.length === 0) {
        data = await fetchStationsByCountry('MX', 30)
      }
      
      setStations(data || [])
      
      if (!data || data.length === 0) {
        setError('No air quality data available. Please check your connection and try again.')
      }
    } catch (err) {
      console.error('Error loading stations:', err)
      setError('Failed to load air quality data. Please try again.')
      setStations([])
    } finally {
      setLoading(false)
    }
  }

  const handleStationSelect = (station) => {
    setSelectedStation(station)
  }

  const handleCloseDetail = () => {
    setSelectedStation(null)
  }

  const handleNotificationClick = () => {
    setIsModalOpen(true)
  }

  const handleLocationObtained = (location) => {
    setUserLocation(location)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setUserLocation(null)
  }

  return (
    <div className="app">
      <Header onNotificationClick={handleNotificationClick} />
      
      <div className="app-content">
        <Sidebar
          stations={stations}
          selectedStation={selectedStation}
          onStationSelect={handleStationSelect}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          loading={loading}
          error={error}
          onRetry={loadStations}
        />

        <MapView
          stations={stations}
          selectedStation={selectedStation}
          onStationSelect={handleStationSelect}
        />

        {selectedStation && (
          <DetailPanel
            station={selectedStation}
            onClose={handleCloseDetail}
          />
        )}
      </div>

      <UserModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onLocationObtained={handleLocationObtained}
        userLocation={userLocation}
      />
    </div>
  )
}

export default App

