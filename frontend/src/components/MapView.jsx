import React, { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import { getAQIColor, getAQICategory } from '../utils/aqi'
import TempoHeatmap from './TempoHeatmap'
import LayerControl from './LayerControl'
import PredictionLayer from './PredictionLayer'
import AnalysisModal from './AnalysisModal'
import 'leaflet/dist/leaflet.css'
import './MapView.css'

// Component to update map view when station is selected
const MapUpdater = ({ selectedStation }) => {
  const map = useMap()
  
  useEffect(() => {
    if (selectedStation) {
      map.flyTo([selectedStation.latitude, selectedStation.longitude], 12, {
        duration: 1.5
      })
    }
  }, [selectedStation, map])
  
  return null
}

const MapView = ({ stations, selectedStation, onStationSelect }) => {
  const mapRef = useRef(null)
  const [layers, setLayers] = useState({
    stations: true,
    tempo: false,
    predictions: false
  })
  const [analysisModalOpen, setAnalysisModalOpen] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)

  const handleToggleLayer = (layerName) => {
    setLayers(prev => ({
      ...prev,
      [layerName]: !prev[layerName]
    }))
  }

  const handleAnalysisClick = (data) => {
    setAnalysisData(data)
    setAnalysisModalOpen(true)
  }

  const handleCloseAnalysis = () => {
    setAnalysisModalOpen(false)
    setAnalysisData(null)
  }

  return (
    <div className="map-view">
      <LayerControl layers={layers} onToggleLayer={handleToggleLayer} />
      
      <MapContainer
        center={[-12.0464, -77.0428]} // Lima, Peru as default
        zoom={6}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        zoomControl={true}
      >
        {/* Dark theme tile layer - CartoDB Dark Matter */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {/* TEMPO satellite heatmap */}
        <TempoHeatmap visible={layers.tempo} parameter="no2" />

        {/* Prediction layer */}
        {layers.predictions && selectedStation && (
          <PredictionLayer 
            station={selectedStation}
            visible={layers.predictions}
            onAnalysisClick={handleAnalysisClick}
          />
        )}

        {/* Station markers */}
        {layers.stations && stations.map((station) => {
          const color = getAQIColor(station.aqi)
          const isSelected = selectedStation?.station_id === station.station_id

          return (
            <CircleMarker
              key={station.station_id}
              center={[station.latitude, station.longitude]}
              radius={isSelected ? 12 : 8}
              fillColor={color}
              color="#ffffff"
              weight={isSelected ? 3 : 2}
              opacity={1}
              fillOpacity={0.8}
              eventHandlers={{
                click: () => onStationSelect(station),
              }}
            >
              <Popup>
                <div className="station-popup">
                  <h3>{station.name}</h3>
                  <div className="popup-aqi">
                    <span className="aqi-value" style={{ color }}>
                      {station.aqi || 'N/A'}
                    </span>
                    <span className="aqi-category">
                      {getAQICategory(station.aqi)}
                    </span>
                  </div>
                  {station.pollutants && (
                    <div className="popup-pollutants">
                      {Object.entries(station.pollutants).map(([key, value]) => (
                        <div key={key} className="pollutant-item">
                          <span className="pollutant-name">{key.toUpperCase()}:</span>
                          <span className="pollutant-value">{value.toFixed(1)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          )
        })}

        <MapUpdater selectedStation={selectedStation} />
      </MapContainer>

      {/* Analysis Modal */}
      <AnalysisModal 
        isOpen={analysisModalOpen}
        onClose={handleCloseAnalysis}
        analysisData={analysisData}
      />

      {/* AQI Legend */}
      <div className="map-legend">
        <h4>Air Quality Index</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#00E400' }}></span>
            <span className="legend-label">Good (0-50)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#FFFF00' }}></span>
            <span className="legend-label">Moderate (51-100)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#FF7E00' }}></span>
            <span className="legend-label">Unhealthy (101-150)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#FF0000' }}></span>
            <span className="legend-label">Unhealthy (151-200)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#8F3F97' }}></span>
            <span className="legend-label">Very Unhealthy (201-300)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#7E0023' }}></span>
            <span className="legend-label">Hazardous (301+)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapView

