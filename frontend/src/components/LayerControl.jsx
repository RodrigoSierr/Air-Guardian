import React from 'react'
import { Layers, Satellite, MapPin, TrendingUp } from 'lucide-react'
import './LayerControl.css'

const LayerControl = ({ layers, onToggleLayer }) => {
  const [expanded, setExpanded] = React.useState(false)

  return (
    <div className={`layer-control ${expanded ? 'expanded' : ''}`}>
      <button 
        className="layer-control-toggle"
        onClick={() => setExpanded(!expanded)}
        title="Toggle layers"
      >
        <Layers size={20} />
      </button>

      {expanded && (
        <div className="layer-control-panel">
          <h3>Map Layers</h3>
          
          <div className="layer-options">
            <label className="layer-option">
              <input
                type="checkbox"
                checked={layers.stations}
                onChange={() => onToggleLayer('stations')}
              />
              <MapPin size={16} />
              <span>Ground Stations</span>
            </label>

            <label className="layer-option">
              <input
                type="checkbox"
                checked={layers.tempo}
                onChange={() => onToggleLayer('tempo')}
              />
              <Satellite size={16} />
              <span>TEMPO Satellite (NO₂)</span>
            </label>

            <label className="layer-option">
              <input
                type="checkbox"
                checked={layers.predictions}
                onChange={() => onToggleLayer('predictions')}
              />
              <TrendingUp size={16} />
              <span>Predicciones</span>
            </label>
          </div>

          <div className="layer-info">
            <p className="info-text">
              <strong>TEMPO:</strong> NASA's satellite air quality data
            </p>
            <p className="info-text">
              <strong>Predicciones:</strong> Análisis predictivo de calidad del aire
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default LayerControl

