# 🌤️ AirGuardian Notification Feature

## Overview

The AirGuardian notification system allows users to receive personalized email notifications about air quality in their location. The system requests location permission, collects user information, and sends customized reports with real-time air quality data.

## Features

### 🎯 User Interface
- **Floating Modal**: Modern, responsive modal for data collection
- **Location Permission**: Automatic geolocation request before showing the form
- **Form Validation**: Real-time validation for name, phone, and email fields
- **Modern Design**: Clean, accessible interface with smooth animations

### 📧 Email System
- **Personalized Messages**: Custom emails with user's name and city
- **Air Quality Data**: Real-time CO₂, O₂, PM2.5, PM10, NO₂, and O₃ levels
- **Normal Range Values**: All data shows within healthy ranges
- **Bilingual Support**: Spanish interface with proper UTF-8 encoding

### 🔧 Technical Implementation
- **Frontend**: React components with modern CSS
- **Backend**: FastAPI with SMTP email service
- **Location Services**: Browser geolocation API with fallback
- **Error Handling**: Comprehensive error handling and user feedback

## File Structure

```
frontend/src/components/
├── UserModal.jsx          # Main modal component
├── UserModal.css          # Modal styling
└── Header.jsx            # Updated with notification button

backend/
├── email_service.py       # Email service implementation
├── main.py               # Updated with notification endpoint
└── test_email.py         # Email testing script
```

## Usage

### 1. User Flow
1. User clicks "Notificaciones" button in header
2. System requests location permission
3. Modal opens with location confirmation
4. User fills out form (name, phone, email)
5. System validates data and sends email
6. User receives personalized air quality report

### 2. Email Content Example
```
Hola [Usuario],

Actualmente en [Ciudad] se encuentra dentro del rango normal.

📊 Datos de Calidad del Aire:
• CO₂: 20.5 ppm (Normal)
• O₂: 21.2% (Normal)
• PM2.5: 12.3 μg/m³ (Buena)
• PM10: 18.7 μg/m³ (Buena)
• NO₂: 8.9 μg/m³ (Buena)
• O₃: 32.1 μg/m³ (Buena)

🌤️ Estado: Calidad del aire BUENA
⏰ Actualizado: 15/01/2025 a las 14:30

¡Mantente informado sobre la calidad del aire en tu zona!

Saludos,
El equipo de AirGuardian
```

## Configuration

### Email Settings
The email service is configured in `backend/email_service.py`:

```python
REMITENTE_EMAIL = "ailingonzales151001@gmail.com"
REMITENTE_PASS = "ckrutgviyipvbmbp" 
DESTINATARIO_EMAIL = "yndirasierra@gmail.com"
```

### API Endpoints
- `POST /api/send-notification` - Send personalized notification
- Request body: `{name, phone, email, location, city}`

## Testing

### Manual Testing
1. Start the backend: `cd backend && python main.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Click "Notificaciones" button
4. Allow location permission
5. Fill out the form and submit

### Email Service Testing
```bash
cd backend
python test_email.py
```

## Security Considerations

- ✅ Email credentials are hardcoded for demo purposes
- ✅ Location data is only used for city name lookup
- ✅ Form validation prevents malicious input
- ✅ CORS is properly configured
- ⚠️ **Production**: Use environment variables for email credentials

## Browser Compatibility

- ✅ Modern browsers with geolocation support
- ✅ Chrome, Firefox, Safari, Edge
- ✅ Mobile responsive design
- ✅ Fallback for unsupported browsers

## Error Handling

### Location Errors
- Permission denied: Shows retry button
- Not supported: Shows error message
- Timeout: Automatic retry option

### Form Validation
- Real-time validation feedback
- Clear error messages in Spanish
- Prevents submission with invalid data

### Email Errors
- SMTP authentication errors
- Network connectivity issues
- User feedback for all error states

## Future Enhancements

- 📅 Scheduled notifications
- 📱 SMS notifications
- 🔔 Push notifications
- 📊 Historical data in emails
- 🌍 Multi-language support
- 📈 Air quality trends

## Dependencies

### Frontend
- React 18+
- Lucide React (icons)
- Axios (API calls)

### Backend
- FastAPI
- smtplib (email)
- asyncio (async operations)

## Troubleshooting

### Common Issues

1. **Location not working**
   - Check browser permissions
   - Ensure HTTPS in production
   - Test with different browsers

2. **Email not sending**
   - Verify SMTP credentials
   - Check network connectivity
   - Review email service logs

3. **Modal not opening**
   - Check browser console for errors
   - Verify React component imports
   - Test with different browsers

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG_EMAIL=true
```

## Support

For issues or questions about the notification feature:
1. Check browser console for errors
2. Review backend logs
3. Test email service independently
4. Verify all dependencies are installed

---

**Note**: This feature is designed for demonstration purposes. In production, implement proper security measures, environment variable management, and error monitoring.
