import React, { useState, useEffect } from 'react'
import { X, BarChart3, TrendingUp, Clock, Download } from 'lucide-react'
import PredictionCharts from './PredictionCharts'
import './AnalysisModal.css'

const AnalysisModal = ({ isOpen, onClose, analysisData }) => {
  const [activeTab, setActiveTab] = useState('overview')
  const [chartData, setChartData] = useState(null)
  const [showPredictionCharts, setShowPredictionCharts] = useState(false)

  useEffect(() => {
    if (analysisData && isOpen) {
      processAnalysisData(analysisData)
    }
  }, [analysisData, isOpen])

  const processAnalysisData = (data) => {
    if (!data) return

    const processedData = {
      stationName: data.station_name || 'Unknown Station',
      analysisType: data.analysis_type,
      timestamp: data.generated_at || new Date().toISOString(),
      charts: data.charts || {},
      data: data.data || {}
    }

    setChartData(processedData)
  }

  const renderTimelineChart = () => {
    if (!chartData || chartData.analysisType !== 'timeline') return null

    const { historical, future } = chartData.data

    return (
      <div className="chart-container">
        <h4>Evolución Temporal de Contaminantes</h4>
        <div className="chart-placeholder">
          <p>📈 Gráfico de Timeline</p>
          <p>Datos históricos: {historical?.length || 0} puntos</p>
          <p>Predicciones futuras: {future?.length || 0} puntos</p>
          <div className="chart-legend">
            <div className="legend-item">
              <span className="legend-color blue"></span>
              <span>Datos Históricos</span>
            </div>
            <div className="legend-item">
              <span className="legend-color red"></span>
              <span>Predicciones Futuras</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const renderImpactChart = () => {
    if (!chartData || chartData.analysisType !== 'impact') return null

    const { comparison } = chartData.data

    return (
      <div className="chart-container">
        <h4>Análisis de Impacto - Comparación Histórico vs Predicciones</h4>
        <div className="impact-comparison">
          {comparison && Object.entries(comparison).map(([pollutant, data]) => (
            <div key={pollutant} className="pollutant-comparison">
              <h5>{pollutant.toUpperCase()}</h5>
              <div className="comparison-values">
                <div className="value-item">
                  <span className="label">Histórico:</span>
                  <span className="value historical">{data.historical?.toFixed(2)}</span>
                </div>
                <div className="value-item">
                  <span className="label">Predicción:</span>
                  <span className="value predicted">{data.predicted?.toFixed(2)}</span>
                </div>
                <div className="value-item">
                  <span className="label">Cambio:</span>
                  <span className={`value change ${data.change_percent > 0 ? 'increase' : 'decrease'}`}>
                    {data.change_percent?.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderInteractiveTimelineChart = () => {
    if (!chartData || chartData.analysisType !== 'interactive_timeline') return null

    const { scenarios } = chartData.data

    return (
      <div className="chart-container">
        <h4>Línea de Tiempo Interactiva - Escenarios Futuros</h4>
        <div className="scenarios-container">
          {scenarios && Object.entries(scenarios).map(([scenarioName, data]) => (
            <div key={scenarioName} className="scenario-card">
              <h5>{scenarioName.replace('_', ' ').toUpperCase()}</h5>
              <div className="scenario-data">
                <p>Puntos de datos: {data.length}</p>
                <div className="scenario-preview">
                  <div className="preview-item">
                    <span>PM2.5 Promedio:</span>
                    <span>{(data.reduce((sum, point) => sum + point.pm25, 0) / data.length).toFixed(2)}</span>
                  </div>
                  <div className="preview-item">
                    <span>PM10 Promedio:</span>
                    <span>{(data.reduce((sum, point) => sum + point.pm10, 0) / data.length).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderChart = () => {
    if (!chartData) return null

    switch (chartData.analysisType) {
      case 'timeline':
        return renderTimelineChart()
      case 'impact':
        return renderImpactChart()
      case 'interactive_timeline':
        return renderInteractiveTimelineChart()
      default:
        return <div>Análisis no disponible</div>
    }
  }

  const handleDownload = () => {
    if (!chartData) return

    const dataToDownload = {
      station_name: chartData.stationName,
      analysis_type: chartData.analysisType,
      timestamp: chartData.timestamp,
      data: chartData.data
    }

    const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analysis_${chartData.stationName}_${chartData.analysisType}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!isOpen || !analysisData) return null

  return (
    <div className="analysis-modal">
      <div className="analysis-modal-content">
        <div className="analysis-modal-header">
          <h2 className="analysis-modal-title">
            {chartData?.stationName} - Análisis de Predicciones
          </h2>
          <button className="analysis-modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="analysis-tabs">
          <button 
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <BarChart3 size={16} />
            Resumen
          </button>
          <button 
            className={`tab-button ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            <TrendingUp size={16} />
            Gráfico
          </button>
          <button 
            className={`tab-button ${activeTab === 'forecast' ? 'active' : ''}`}
            onClick={() => setActiveTab('forecast')}
          >
            <Clock size={16} />
            Forecast
          </button>
          <button 
            className={`tab-button ${activeTab === 'data' ? 'active' : ''}`}
            onClick={() => setActiveTab('data')}
          >
            <Download size={16} />
            Datos
          </button>
        </div>

        <div className="analysis-content">
          {activeTab === 'overview' && (
            <div className="overview-section">
              <div className="overview-cards">
                <div className="overview-card">
                  <h4>Tipo de Análisis</h4>
                  <p>{chartData?.analysisType?.replace('_', ' ').toUpperCase()}</p>
                </div>
                <div className="overview-card">
                  <h4>Estación</h4>
                  <p>{chartData?.stationName}</p>
                </div>
                <div className="overview-card">
                  <h4>Generado</h4>
                  <p>{new Date(chartData?.timestamp).toLocaleString()}</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chart' && (
            <div className="chart-section">
              {renderChart()}
            </div>
          )}

          {activeTab === 'forecast' && (
            <div className="forecast-section">
              <div className="forecast-header">
                <h3>Análisis de Predicciones Detalladas</h3>
                <p>Visualización de datos históricos (azul) vs predicciones (rojo) para PM2.5, PM10, NO2 y O3</p>
              </div>
              
              <div className="forecast-charts-container">
                <div className="charts-navigation">
                  <button 
                    className="nav-btn active"
                    onClick={() => console.log('Análisis de Impacto')}
                  >
                    <BarChart3 size={16} />
                    Análisis de Impacto
                  </button>
                  <button 
                    className="nav-btn"
                    onClick={() => console.log('Timeline')}
                  >
                    <TrendingUp size={16} />
                    Timeline
                  </button>
                  <button 
                    className="nav-btn"
                    onClick={() => console.log('Comparación')}
                  >
                    <Clock size={16} />
                    Comparación
                  </button>
                </div>
                
                <div className="chart-placeholder">
                  <h4>📊 Gráfico de Análisis de Impacto</h4>
                  <p>Comparación entre datos históricos (azul) y predicciones (rojo)</p>
                  <div className="chart-legend">
                    <div className="legend-item">
                      <span className="legend-color blue"></span>
                      <span>Datos Históricos (2020)</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color red"></span>
                      <span>Predicciones (2023-2024)</span>
                    </div>
                  </div>
                  <div className="pollutants-grid">
                    <div className="pollutant-card">
                      <h5>PM2.5</h5>
                      <div className="value-comparison">
                        <span className="historical">15.2 μg/m³</span>
                        <span className="predicted">18.7 μg/m³</span>
                      </div>
                    </div>
                    <div className="pollutant-card">
                      <h5>PM10</h5>
                      <div className="value-comparison">
                        <span className="historical">24.1 μg/m³</span>
                        <span className="predicted">29.8 μg/m³</span>
                      </div>
                    </div>
                    <div className="pollutant-card">
                      <h5>NO₂</h5>
                      <div className="value-comparison">
                        <span className="historical">0.012 ppm</span>
                        <span className="predicted">0.015 ppm</span>
                      </div>
                    </div>
                    <div className="pollutant-card">
                      <h5>O₃</h5>
                      <div className="value-comparison">
                        <span className="historical">0.035 ppm</span>
                        <span className="predicted">0.042 ppm</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="data-section">
              <div className="data-actions">
                <button className="download-btn" onClick={handleDownload}>
                  <Download size={16} />
                  Descargar Datos
                </button>
              </div>
              <div className="data-content">
                <pre>{JSON.stringify(chartData?.data, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  )
}

export default AnalysisModal
