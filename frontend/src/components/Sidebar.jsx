import React, { useState } from 'react'
import { ChevronLeft, ChevronRight, RefreshCw, Search, MapPin } from 'lucide-react'
import { getAQIColor, getAQICategory } from '../utils/aqi'
import './Sidebar.css'

const Sidebar = ({ 
  stations, 
  selectedStation, 
  onStationSelect, 
  collapsed, 
  onToggleCollapse,
  loading,
  error,
  onRetry
}) => {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredStations = stations.filter(station =>
    station.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const sortedStations = [...filteredStations].sort((a, b) => {
    if (a.aqi === null) return 1
    if (b.aqi === null) return -1
    return b.aqi - a.aqi
  })

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <button 
        className="sidebar-toggle"
        onClick={onToggleCollapse}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>

      {!collapsed && (
        <div className="sidebar-content">
          <div className="sidebar-header">
            <h2>Monitoring Stations</h2>
            <button 
              className="refresh-button"
              onClick={onRetry}
              disabled={loading}
              aria-label="Refresh data"
            >
              <RefreshCw size={18} className={loading ? 'spinning' : ''} />
            </button>
          </div>

          <div className="search-box">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search stations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={onRetry} className="retry-button">
                Retry
              </button>
            </div>
          )}

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading stations...</p>
            </div>
          ) : (
            <div className="stations-list">
              {sortedStations.length === 0 ? (
                <div className="no-stations">
                  <MapPin size={48} />
                  <p>No stations found</p>
                </div>
              ) : (
                sortedStations.map((station) => (
                  <div
                    key={station.station_id}
                    className={`station-card ${
                      selectedStation?.station_id === station.station_id ? 'selected' : ''
                    }`}
                    onClick={() => onStationSelect(station)}
                  >
                    <div className="station-card-header">
                      <h3 className="station-name">{station.name}</h3>
                      <div 
                        className="station-aqi"
                        style={{ 
                          backgroundColor: getAQIColor(station.aqi),
                          color: station.aqi && station.aqi <= 100 ? '#000' : '#fff'
                        }}
                      >
                        {station.aqi || 'N/A'}
                      </div>
                    </div>
                    
                    <div className="station-category">
                      {getAQICategory(station.aqi)}
                    </div>

                    {station.pollutants && (
                      <div className="station-pollutants">
                        {Object.entries(station.pollutants).slice(0, 3).map(([key, value]) => (
                          <span key={key} className="pollutant-badge">
                            {key.toUpperCase()}: {value.toFixed(1)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Sidebar

