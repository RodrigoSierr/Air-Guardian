import React, { useEffect, useState } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import api from '../services/api'

const TempoHeatmap = ({ visible, parameter = 'no2' }) => {
  const map = useMap()
  const [heatmapLayer, setHeatmapLayer] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (visible) {
      loadTempoData()
    } else if (heatmapLayer) {
      map.removeLayer(heatmapLayer)
      setHeatmapLayer(null)
    }
  }, [visible, parameter, map])

  const loadTempoData = async () => {
    setLoading(true)
    
    try {
      // Get map bounds
      const bounds = map.getBounds()
      
      const response = await api.get('/api/tempo/grid', {
        params: {
          parameter,
          lat_min: bounds.getSouth(),
          lat_max: bounds.getNorth(),
          lon_min: bounds.getWest(),
          lon_max: bounds.getEast()
        }
      })

      const data = response.data.data

      // Convert to heatmap format
      const heatmapData = data.map(point => [
        point.latitude,
        point.longitude,
        point.value / 50 // Normalize intensity
      ])

      // Remove old layer if exists
      if (heatmapLayer) {
        map.removeLayer(heatmapLayer)
      }

      // Create new heatmap layer
      const newLayer = L.heatLayer(heatmapData, {
        radius: 25,
        blur: 35,
        maxZoom: 10,
        max: 1.0,
        gradient: {
          0.0: '#0000FF',  // Blue - Low
          0.2: '#00FFFF',  // Cyan
          0.4: '#00FF00',  // Green
          0.6: '#FFFF00',  // Yellow
          0.8: '#FF7F00',  // Orange
          1.0: '#FF0000'   // Red - High
        }
      })

      newLayer.addTo(map)
      setHeatmapLayer(newLayer)
    } catch (error) {
      console.error('Error loading TEMPO data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (heatmapLayer && map) {
        map.removeLayer(heatmapLayer)
      }
    }
  }, [])

  return null // This component doesn't render anything directly
}

export default TempoHeatmap

