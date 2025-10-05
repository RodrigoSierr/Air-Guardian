import React from 'react'
import { Wind, Bell } from 'lucide-react'
import './Header.css'

const Header = ({ onNotificationClick }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <Wind className="header-icon" size={28} />
          <h1 className="header-title">AirGuardian</h1>
          <span className="header-subtitle">Real-time Air Quality Monitoring</span>
        </div>
        
        <div className="header-right">
          <div className="header-info">
            <span className="info-label">Last Update:</span>
            <span className="info-value">{new Date().toLocaleTimeString()}</span>
          </div>
          <button 
            className="notification-button"
            onClick={onNotificationClick}
            title="Configurar notificaciones"
          >
            <Bell size={20} />
            <span>Notificaciones</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header

