import React, { useState, useEffect } from 'react'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import DetailPanel from './components/DetailPanel'
import Header from './components/Header'
import { fetchStations } from './services/api'
import './App.css'

function App() {
  const [stations, setStations] = useState([])
  const [selectedStation, setSelectedStation] = useState(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadStations()
  }, [])

  const loadStations = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchStations()
      setStations(data)
    } catch (err) {
      console.error('Error loading stations:', err)
      setError('Failed to load air quality data. Please try again.')
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

  return (
    <div className="app">
      <Header />
      
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
    </div>
  )
}

export default App

