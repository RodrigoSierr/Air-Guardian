import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Clock, Download, X } from 'lucide-react'
import './PredictionCharts.css'

const PredictionCharts = ({ station, isOpen, onClose }) => {
  const [activeChart, setActiveChart] = useState('impact')
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (station && isOpen) {
      loadChartData()
    }
  }, [station, isOpen, activeChart])

  const loadChartData = async () => {
    if (!station) return

    setLoading(true)
    setError(null)

    try {
      console.log('Loading chart data for station:', station.station_id, 'chart type:', activeChart)
      
      const response = await fetch('/api/prediction-charts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          station_id: station.station_id || station.id || 'station_1',
          chart_type: activeChart,
          pollutants: ['PM2_5', 'PM10', 'NO2', 'O3']
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('API Error:', response.status, errorText)
        throw new Error(`API Error: ${response.status} - ${errorText}`)
      }

      const data = await response.json()
      console.log('Chart data loaded:', data)
      setChartData(data)
      
    } catch (err) {
      console.error('Error loading chart data:', err)
      setError(`Error cargando gráfico: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleChartTypeChange = (chartType) => {
    setActiveChart(chartType)
  }

  const handleDownloadChart = async () => {
    if (!station || !activeChart) return

    try {
      const response = await fetch(`/api/prediction-charts/${station.station_id}/${activeChart}`)
      if (!response.ok) {
        throw new Error('Failed to download chart')
      }

      const htmlContent = await response.text()
      const blob = new Blob([htmlContent], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      
      const a = document.createElement('a')
      a.href = url
      a.download = `prediction_chart_${station.station_id}_${activeChart}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
    } catch (err) {
      console.error('Error downloading chart:', err)
      alert('Error downloading chart')
    }
  }

  const renderChart = () => {
    if (loading) {
      return (
        <div className="chart-loading">
          <div className="loading-spinner"></div>
          <p>Cargando gráfico...</p>
        </div>
      )
    }

    if (error) {
      return (
        <div className="chart-error">
          <p>Error cargando el gráfico: {error}</p>
          <button onClick={loadChartData} className="retry-btn">
            Reintentar
          </button>
        </div>
      )
    }

    if (!chartData) {
      return (
        <div className="chart-empty">
          <p>No hay datos disponibles para mostrar</p>
        </div>
      )
    }

    return (
      <div className="chart-container">
        <div 
          className="chart-content"
          dangerouslySetInnerHTML={{ __html: chartData.html_content }}
        />
        <div className="chart-info">
          <p><strong>Estación:</strong> {chartData.data_summary?.station_name || 'N/A'}</p>
          <p><strong>Registros:</strong> {chartData.data_summary?.total_records || 0}</p>
          <p><strong>Tipo:</strong> {getChartTitle()}</p>
        </div>
      </div>
    )
  }

  const getChartTitle = () => {
    const titles = {
      impact: 'Análisis de Impacto',
      timeline: 'Timeline de Contaminantes',
      comparison: 'Comparación de Escenarios'
    }
    return titles[activeChart] || 'Gráfico de Predicciones'
  }

  const getChartDescription = () => {
    const descriptions = {
      impact: 'Comparación entre datos históricos (azul) y predicciones (rojo)',
      timeline: 'Evolución temporal de la calidad del aire',
      comparison: 'Proyecciones futuras basadas en el modelo entrenado'
    }
    return descriptions[activeChart] || ''
  }

  if (!isOpen || !station) return null

  return (
    <div className="prediction-charts-integrated">
      <div className="prediction-charts-content">
        <div className="charts-header">
          <div className="header-info">
            <h2>Gráficos de Predicciones</h2>
            <p>{station.name || station.station_name || 'Estación'} - {getChartTitle()}</p>
            <p className="chart-description">{getChartDescription()}</p>
          </div>
          <div className="header-actions">
            <button 
              className="download-btn"
              onClick={handleDownloadChart}
              title="Descargar gráfico"
            >
              <Download size={16} />
            </button>
            {onClose && (
              <button 
                className="close-btn"
                onClick={onClose}
                title="Cerrar"
              >
                <X size={20} />
              </button>
            )}
          </div>
        </div>

        <div className="charts-navigation">
          <button 
            className={`nav-btn ${activeChart === 'impact' ? 'active' : ''}`}
            onClick={() => handleChartTypeChange('impact')}
          >
            <BarChart3 size={16} />
            Análisis de Impacto
          </button>
          <button 
            className={`nav-btn ${activeChart === 'timeline' ? 'active' : ''}`}
            onClick={() => handleChartTypeChange('timeline')}
          >
            <TrendingUp size={16} />
            Timeline
          </button>
          <button 
            className={`nav-btn ${activeChart === 'comparison' ? 'active' : ''}`}
            onClick={() => handleChartTypeChange('comparison')}
          >
            <Clock size={16} />
            Comparación
          </button>
        </div>

        <div className="charts-content">
          {renderChart()}
        </div>

        {chartData && chartData.data_summary && (
          <div className="charts-summary">
            <h4>Resumen de Datos</h4>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="label">Estación:</span>
                <span className="value">{chartData.data_summary.station_name}</span>
              </div>
              <div className="summary-item">
                <span className="label">Registros:</span>
                <span className="value">{chartData.data_summary.total_records}</span>
              </div>
              <div className="summary-item">
                <span className="label">Período:</span>
                <span className="value">
                  {new Date(chartData.data_summary.date_range.start).toLocaleDateString()} - 
                  {new Date(chartData.data_summary.date_range.end).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictionCharts
