import React, { useState, useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import { BarChart3, TrendingUp, Clock, MapPin, Layers } from 'lucide-react'
import './PredictionLayer.css'

const PredictionLayer = ({ station, visible, onAnalysisClick }) => {
  const map = useMap()
  const [predictionData, setPredictionData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [heatmapLayer, setHeatmapLayer] = useState(null)
  const [markers, setMarkers] = useState([])

  useEffect(() => {
    if (station && visible) {
      loadPredictionData()
    } else {
      clearLayers()
    }
  }, [station, visible])

  const loadPredictionData = async () => {
    if (!station) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/prediction-layer/${station.station_id}`)
      if (!response.ok) {
        throw new Error('Failed to load prediction data')
      }
      
      const data = await response.json()
      setPredictionData(data)
      
      // Create heatmap layer
      createHeatmapLayer(data.heatmap_data)
      
      // Create prediction markers
      createPredictionMarkers(data.predictions)
      
    } catch (err) {
      console.error('Error loading prediction data:', err)
      setError('Failed to load prediction data')
    } finally {
      setLoading(false)
    }
  }

  const createHeatmapLayer = (heatmapData) => {
    if (heatmapLayer) {
      map.removeLayer(heatmapLayer)
    }

    if (heatmapData && heatmapData.length > 0) {
      const points = heatmapData.map(point => [
        point.latitude,
        point.longitude,
        point.value
      ])

      const heatmap = L.heatLayer(points, {
        radius: 25,
        blur: 15,
        maxZoom: 10,
        gradient: {
          0.0: 'blue',
          0.5: 'yellow',
          1.0: 'red'
        }
      })

      heatmap.addTo(map)
      setHeatmapLayer(heatmap)
    }
  }

  const createPredictionMarkers = (predictions) => {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker))
    const newMarkers = []

    if (predictions && predictions.length > 0) {
      // Create marker for the station with prediction data
      const latestPrediction = predictions[predictions.length - 1]
      
      const predictionIcon = L.divIcon({
        html: `
          <div class="prediction-marker">
            <div class="prediction-value">${latestPrediction.pm25.toFixed(1)}</div>
            <div class="prediction-label">PM2.5</div>
          </div>
        `,
        className: 'prediction-marker-container',
        iconSize: [40, 40],
        iconAnchor: [20, 20]
      })

      const marker = L.marker([station.latitude, station.longitude], {
        icon: predictionIcon
      })

      // Create popup with prediction details and analysis buttons
      const popupContent = createPredictionPopup(latestPrediction, predictions)
      marker.bindPopup(popupContent, { maxWidth: 400 })
      
      marker.addTo(map)
      newMarkers.push(marker)
    }

    setMarkers(newMarkers)
  }

  const createPredictionPopup = (latestPrediction, allPredictions) => {
    const popup = document.createElement('div')
    popup.className = 'prediction-popup'
    
    popup.innerHTML = `
      <div class="prediction-popup-content">
        <h3>${station.name}</h3>
        <div class="prediction-summary">
          <div class="prediction-item">
            <span class="prediction-label">PM2.5:</span>
            <span class="prediction-value">${latestPrediction.pm25.toFixed(1)} μg/m³</span>
          </div>
          <div class="prediction-item">
            <span class="prediction-label">PM10:</span>
            <span class="prediction-value">${latestPrediction.pm10.toFixed(1)} μg/m³</span>
          </div>
          <div class="prediction-item">
            <span class="prediction-label">NO₂:</span>
            <span class="prediction-value">${latestPrediction.no2.toFixed(3)} ppm</span>
          </div>
          <div class="prediction-item">
            <span class="prediction-label">O₃:</span>
            <span class="prediction-value">${latestPrediction.o3.toFixed(3)} ppm</span>
          </div>
          <div class="prediction-item">
            <span class="prediction-label">SO₂:</span>
            <span class="prediction-value">${latestPrediction.so2.toFixed(4)} ppm</span>
          </div>
        </div>
        <div class="prediction-actions">
          <button class="analysis-btn timeline-btn" data-analysis="timeline">
            <TrendingUp size={16} />
            Timeline
          </button>
          <button class="analysis-btn impact-btn" data-analysis="impact">
            <BarChart3 size={16} />
            Análisis Impacto
          </button>
          <button class="analysis-btn interactive-btn" data-analysis="interactive_timeline">
            <Clock size={16} />
            Línea Tiempo
          </button>
        </div>
        <div class="prediction-info">
          <small>Confianza: ${(latestPrediction.confidence * 100).toFixed(1)}%</small>
          <small>Predicciones: ${allPredictions.length} puntos</small>
        </div>
      </div>
    `

    // Add event listeners to buttons
    popup.addEventListener('click', (e) => {
      if (e.target.classList.contains('analysis-btn')) {
        const analysisType = e.target.dataset.analysis
        handleAnalysisClick(analysisType)
      }
    })

    return popup
  }

  const handleAnalysisClick = async (analysisType) => {
    if (!station) return

    try {
      const response = await fetch('/api/prediction-layer/analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          station_id: station.station_id,
          analysis_type: analysisType
        })
      })

      if (!response.ok) {
        throw new Error('Failed to load analysis data')
      }

      const analysisData = await response.json()
      
      // Call parent component to show analysis
      if (onAnalysisClick) {
        onAnalysisClick(analysisData)
      }
      
    } catch (err) {
      console.error('Error loading analysis:', err)
      alert('Error loading analysis data')
    }
  }

  const clearLayers = () => {
    if (heatmapLayer) {
      map.removeLayer(heatmapLayer)
      setHeatmapLayer(null)
    }
    
    markers.forEach(marker => map.removeLayer(marker))
    setMarkers([])
  }

  // Don't render anything - this component manages map layers
  return null
}

export default PredictionLayer
