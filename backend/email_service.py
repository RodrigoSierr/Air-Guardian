import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import asyncio
from typing import Dict, Any

# --- CONFIGURACIÓN DEL CORREO ---
REMITENTE_EMAIL = "ailingonzales151001@gmail.com"
REMITENTE_PASS = "ckrutgviyipvbmbp" 
DESTINATARIO_EMAIL = "yndirasierra@gmail.com"

class EmailService:
    def __init__(self):
        self.sender_email = REMITENTE_EMAIL
        self.sender_password = REMITENTE_PASS
        self.default_recipient = DESTINATARIO_EMAIL

    def generate_air_quality_data(self) -> Dict[str, Any]:
        """Generate realistic air quality data for the email"""
        # Generate normal range values
        co2 = round(random.uniform(18, 25), 1)  # Normal CO2 levels
        o2 = round(random.uniform(20, 22), 1)    # Normal O2 levels
        pm25 = round(random.uniform(8, 15), 1)  # Good PM2.5 levels
        pm10 = round(random.uniform(12, 20), 1) # Good PM10 levels
        no2 = round(random.uniform(5, 15), 1)  # Good NO2 levels
        o3 = round(random.uniform(20, 40), 1)   # Good O3 levels
        
        return {
            "co2": co2,
            "o2": o2,
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "o3": o3
        }

    def create_personalized_message(self, name: str, city: str, air_quality: Dict[str, Any]) -> str:
        """Create a personalized email message with air quality data"""
        message = f"""Hola {name},

Actualmente en {city} se encuentra dentro del rango normal.

📊 Datos de Calidad del Aire:
• CO₂: {air_quality['co2']} ppm (Normal)
• O₂: {air_quality['o2']}% (Normal)
• PM2.5: {air_quality['pm25']} μg/m³ (Buena)
• PM10: {air_quality['pm10']} μg/m³ (Buena)
• NO₂: {air_quality['no2']} μg/m³ (Buena)
• O₃: {air_quality['o3']} μg/m³ (Buena)

🌤️ Estado: Calidad del aire BUENA
⏰ Actualizado: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

¡Mantente informado sobre la calidad del aire en tu zona!

Saludos,
El equipo de AirGuardian
        """
        return message

    async def send_notification(self, user_data: Dict[str, Any]) -> bool:
        """
        Send personalized air quality notification email
        """
        try:
            print(f"📧 Preparando notificación para: {user_data.get('name', 'Usuario')}")
            print(f"📧 Email destino: {user_data.get('email', 'No especificado')}")
            print(f"📍 Ciudad: {user_data.get('city', 'No especificada')}")
            
            # Validate required fields
            if not user_data.get('email'):
                print("❌ Error: Email no proporcionado")
                return False
            
            if not user_data.get('name'):
                print("❌ Error: Nombre no proporcionado")
                return False
            
            # Generate air quality data
            air_quality = self.generate_air_quality_data()
            print(f"📊 Datos generados: CO₂={air_quality['co2']}, O₂={air_quality['o2']}")
            
            # Create personalized message
            message_body = self.create_personalized_message(
                user_data['name'],
                user_data.get('city', 'tu ubicación'),
                air_quality
            )
            
            # Create email
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = user_data['email']
            message["Subject"] = f"🌤️ Reporte de Calidad del Aire - {user_data.get('city', 'Tu ubicación')}"
            
            message.attach(MIMEText(message_body, "plain", "utf-8"))
            print("📝 Mensaje creado exitosamente")

            # Send email
            server_smtp = None
            try:
                print("🔌 Conectando a Gmail SMTP...")
                server_smtp = smtplib.SMTP("smtp.gmail.com", 587)
                print("✅ Conectado a Gmail SMTP")
                
                print("🔒 Iniciando TLS...")
                server_smtp.starttls()
                print("✅ TLS iniciado")
                
                print("🔑 Autenticando...")
                server_smtp.login(self.sender_email, self.sender_password)
                print("✅ Autenticación exitosa")
                
                print("📤 Enviando email...")
                text_message = message.as_string()
                server_smtp.sendmail(self.sender_email, user_data['email'], text_message)
                print(f"✅ ¡Correo enviado exitosamente a {user_data['email']}!")
                
                # Also send to default recipient for backup
                if user_data['email'] != self.default_recipient:
                    print("📋 Enviando copia de respaldo...")
                    message["To"] = self.default_recipient
                    message["Subject"] = f"🌤️ Reporte de Calidad del Aire - {user_data['name']} en {user_data.get('city', 'ubicación')}"
                    text_message = message.as_string()
                    server_smtp.sendmail(self.sender_email, self.default_recipient, text_message)
                    print(f"✅ ¡Copia enviada a {self.default_recipient}!")
                
                return True

            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ Error de autenticación: {e}")
                print("💡 Verifica:")
                print("   - Email: ailingonzales151001@gmail.com")
                print("   - Contraseña de aplicación: ckrutgviyipvbmbp")
                print("   - Verificar que la contraseña de aplicación esté activa")
                return False

            except smtplib.SMTPRecipientsRefused as e:
                print(f"❌ Error: Destinatario rechazado: {e}")
                print(f"💡 Verifica que el email {user_data['email']} sea válido")
                return False

            except smtplib.SMTPException as e:
                print(f"❌ Error SMTP: {e}")
                return False

            except Exception as e:
                print(f"❌ Error inesperado al enviar: {e}")
                print(f"💡 Tipo de error: {type(e).__name__}")
                return False

            finally:
                if server_smtp:
                    try:
                        server_smtp.quit()
                        print("🔌 Conexión SMTP cerrada")
                    except:
                        pass
                    
        except Exception as e:
            print(f"❌ Error general: {e}")
            print(f"💡 Tipo de error: {type(e).__name__}")
            return False

    def send_scheduled_notification(self):
        """Send a scheduled notification (for testing)"""
        try:
            print("Enviando notificación programada...")
            air_quality = self.generate_air_quality_data()
            message_body = f"""Reporte de Calidad del Aire Programado

📊 Datos actuales:
• CO₂: {air_quality['co2']} ppm (Normal)
• O₂: {air_quality['o2']}% (Normal)
• PM2.5: {air_quality['pm25']} μg/m³ (Buena)
• PM10: {air_quality['pm10']} μg/m³ (Buena)
• NO₂: {air_quality['no2']} μg/m³ (Buena)
• O₃: {air_quality['o3']} μg/m³ (Buena)

⏰ {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

El equipo de AirGuardian
            """
            
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.default_recipient
            message["Subject"] = "🌤️ Reporte Programado de Calidad del Aire"
            message.attach(MIMEText(message_body, "plain", "utf-8"))

            server_smtp = smtplib.SMTP("smtp.gmail.com", 587)
            server_smtp.starttls()
            server_smtp.login(self.sender_email, self.sender_password)
            
            text_message = message.as_string()
            server_smtp.sendmail(self.sender_email, self.default_recipient, text_message)
            print(f"✅ ¡Notificación programada enviada exitosamente!")
            server_smtp.quit()

        except Exception as e:
            print(f"❌ Error al enviar notificación programada: {e}")

# Global email service instance
email_service = EmailService()

def setup_scheduled_notifications():
    """Setup scheduled email notifications"""
    print("Configurando notificaciones programadas...")
    
    # Schedule notifications every 2 hours
    schedule.every(2).hours.do(email_service.send_scheduled_notification)
    
    # Send initial notification
    email_service.send_scheduled_notification()
    
    print("Notificaciones programadas configuradas. Próxima notificación en 2 horas.")

def run_scheduler():
    """Run the email scheduler in a separate thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# For testing purposes
if __name__ == "__main__":
    # Test the email service
    test_user_data = {
        "name": "Usuario de Prueba",
        "email": "test@example.com",
        "phone": "+1234567890",
        "city": "Lima",
        "location": {"latitude": -12.0464, "longitude": -77.0428}
    }
    
    # Test sending notification
    asyncio.run(email_service.send_notification(test_user_data))
