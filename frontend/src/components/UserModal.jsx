import React, { useState, useEffect } from 'react'
import { X, MapPin, User, Phone, Mail, Send, AlertCircle } from 'lucide-react'
import { sendNotification } from '../services/api'
import './UserModal.css'

const UserModal = ({ isOpen, onClose, onLocationObtained, userLocation }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: ''
  })
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [locationPermission, setLocationPermission] = useState(null)
  const [cityName, setCityName] = useState('')

  useEffect(() => {
    if (isOpen) {
      requestLocationPermission()
    }
  }, [isOpen])

  const requestLocationPermission = async () => {
    if (!navigator.geolocation) {
      setLocationPermission('not_supported')
      return
    }

    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000
        })
      })

      const { latitude, longitude } = position.coords
      onLocationObtained({ latitude, longitude })
      setLocationPermission('granted')
      
      // Get city name from coordinates
      await getCityName(latitude, longitude)
    } catch (error) {
      console.error('Error getting location:', error)
      setLocationPermission('denied')
    }
  }

  const getCityName = async (lat, lon) => {
    try {
      const response = await fetch(
        `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=es`
      )
      const data = await response.json()
      setCityName(data.city || data.locality || 'tu ubicación')
    } catch (error) {
      console.error('Error getting city name:', error)
      setCityName('tu ubicación')
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido'
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'El nombre debe tener al menos 2 caracteres'
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'El número de teléfono es requerido'
    } else if (!/^[\d\s\-\+\(\)]+$/.test(formData.phone.trim())) {
      newErrors.phone = 'Formato de teléfono inválido'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El correo electrónico es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      newErrors.email = 'Formato de correo electrónico inválido'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    if (locationPermission !== 'granted') {
      alert('Por favor, permite el acceso a tu ubicación para continuar')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await sendNotification({
        ...formData,
        location: userLocation,
        city: cityName
      })

      if (response.status === 'success') {
        alert('¡Notificación enviada exitosamente!')
        onClose()
        setFormData({ name: '', phone: '', email: '' })
      } else {
        throw new Error('Error al enviar la notificación')
      }
    } catch (error) {
      console.error('Error sending notification:', error)
      alert('Error al enviar la notificación. Por favor, intenta de nuevo.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    setFormData({ name: '', phone: '', email: '' })
    setErrors({})
    setLocationPermission(null)
    setCityName('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2>Configurar Notificaciones</h2>
          <button className="close-button" onClick={handleClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          {locationPermission === null && (
            <div className="location-request">
              <MapPin className="location-icon" size={24} />
              <p>Solicitando acceso a tu ubicación...</p>
            </div>
          )}

          {locationPermission === 'denied' && (
            <div className="location-error">
              <AlertCircle className="error-icon" size={24} />
              <p>No se pudo acceder a tu ubicación. Por favor, permite el acceso a la ubicación en tu navegador.</p>
              <button 
                className="retry-button"
                onClick={requestLocationPermission}
              >
                Reintentar
              </button>
            </div>
          )}

          {locationPermission === 'not_supported' && (
            <div className="location-error">
              <AlertCircle className="error-icon" size={24} />
              <p>Tu navegador no soporta geolocalización.</p>
            </div>
          )}

          {locationPermission === 'granted' && (
            <div className="location-success">
              <MapPin className="success-icon" size={24} />
              <p>Ubicación obtenida: {cityName}</p>
            </div>
          )}

          {locationPermission === 'granted' && (
            <form onSubmit={handleSubmit} className="user-form">
              <div className="form-group">
                <label htmlFor="name">
                  <User size={16} />
                  Nombre completo
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className={errors.name ? 'error' : ''}
                  placeholder="Ingresa tu nombre completo"
                />
                {errors.name && <span className="error-message">{errors.name}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="phone">
                  <Phone size={16} />
                  Número de teléfono
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className={errors.phone ? 'error' : ''}
                  placeholder="+1 (555) 123-4567"
                />
                {errors.phone && <span className="error-message">{errors.phone}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="email">
                  <Mail size={16} />
                  Correo electrónico
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={errors.email ? 'error' : ''}
                  placeholder="tu@email.com"
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={handleClose}
                  className="cancel-button"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="submit-button"
                >
                  {isSubmitting ? (
                    <>
                      <div className="spinner"></div>
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Enviar Notificación
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserModal
