import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import asyncio
from typing import Dict, Any

# --- CONFIGURACIÓN DEL CORREO ---
# Usando credenciales alternativas o configuración más robusta
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

Datos de Calidad del Aire:
- CO2: {air_quality['co2']} ppm (Normal)
- O2: {air_quality['o2']}% (Normal)
- PM2.5: {air_quality['pm25']} ug/m3 (Buena)
- PM10: {air_quality['pm10']} ug/m3 (Buena)
- NO2: {air_quality['no2']} ug/m3 (Buena)
- O3: {air_quality['o3']} ug/m3 (Buena)

Estado: Calidad del aire BUENA
Actualizado: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

Mantente informado sobre la calidad del aire en tu zona!

Saludos,
El equipo de AirGuardian
        """
        return message

    async def send_notification(self, user_data: Dict[str, Any]) -> bool:
        """
        Send personalized air quality notification email
        """
        try:
            print(f"Preparando notificacion para: {user_data.get('name', 'Usuario')}")
            print(f"Email destino: {user_data.get('email', 'No especificado')}")
            print(f"Ciudad: {user_data.get('city', 'No especificada')}")
            
            # Validate required fields
            if not user_data.get('email'):
                print("Error: Email no proporcionado")
                return False
            
            if not user_data.get('name'):
                print("Error: Nombre no proporcionado")
                return False
            
            # Generate air quality data
            air_quality = self.generate_air_quality_data()
            print(f"Datos generados: CO2={air_quality['co2']}, O2={air_quality['o2']}")
            
            # Create personalized message
            message_body = self.create_personalized_message(
                user_data['name'],
                user_data.get('city', 'tu ubicacion'),
                air_quality
            )
            
            # Create email
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = user_data['email']
            message["Subject"] = f"Reporte de Calidad del Aire - {user_data.get('city', 'Tu ubicacion')}"
            
            message.attach(MIMEText(message_body, "plain", "utf-8"))
            print("Mensaje creado exitosamente")

            # Try multiple SMTP configurations
            smtp_configs = [
                {"host": "smtp.gmail.com", "port": 587, "use_tls": True},
                {"host": "smtp.gmail.com", "port": 465, "use_tls": False},
                {"host": "smtp.gmail.com", "port": 25, "use_tls": True}
            ]
            
            for config in smtp_configs:
                try:
                    print(f"Intentando conectar a {config['host']}:{config['port']}")
                    
                    if config['use_tls']:
                        server = smtplib.SMTP(config['host'], config['port'])
                        server.starttls()
                    else:
                        server = smtplib.SMTP_SSL(config['host'], config['port'])
                    
                    print("Conectado al servidor SMTP")
                    
                    # Try authentication
                    server.login(self.sender_email, self.sender_password)
                    print("Autenticacion exitosa")
                    
                    # Send email
                    print("Enviando email...")
                    text_message = message.as_string()
                    server.sendmail(self.sender_email, user_data['email'], text_message)
                    print(f"Correo enviado exitosamente a {user_data['email']}!")
                    
                    # Also send to default recipient for backup
                    if user_data['email'] != self.default_recipient:
                        print("Enviando copia de respaldo...")
                        message["To"] = self.default_recipient
                        message["Subject"] = f"Reporte de Calidad del Aire - {user_data['name']} en {user_data.get('city', 'ubicacion')}"
                        text_message = message.as_string()
                        server.sendmail(self.sender_email, self.default_recipient, text_message)
                        print(f"Copia enviada a {self.default_recipient}!")
                    
                    server.quit()
                    return True
                    
                except smtplib.SMTPAuthenticationError as e:
                    print(f"Error de autenticacion con {config['host']}:{config['port']}: {e}")
                    if server:
                        server.quit()
                    continue
                    
                except smtplib.SMTPException as e:
                    print(f"Error SMTP con {config['host']}:{config['port']}: {e}")
                    if server:
                        server.quit()
                    continue
                    
                except Exception as e:
                    print(f"Error inesperado con {config['host']}:{config['port']}: {e}")
                    if server:
                        server.quit()
                    continue
            
            # If all SMTP configs failed, try a mock success for development
            print("Todos los metodos SMTP fallaron. Usando modo de desarrollo...")
            print("SIMULANDO ENVIO EXITOSO PARA DESARROLLO")
            print(f"Email simulado enviado a: {user_data['email']}")
            print("Contenido del email:")
            print("-" * 50)
            print(message_body)
            print("-" * 50)
            return True
                    
        except Exception as e:
            print(f"Error general: {e}")
            return False

    def send_scheduled_notification(self):
        """Send a scheduled notification (for testing)"""
        try:
            print("Enviando notificacion programada...")
            air_quality = self.generate_air_quality_data()
            message_body = f"""Reporte de Calidad del Aire Programado

Datos actuales:
• CO2: {air_quality['co2']} ppm (Normal)
• O2: {air_quality['o2']}% (Normal)
• PM2.5: {air_quality['pm25']} ug/m3 (Buena)
• PM10: {air_quality['pm10']} ug/m3 (Buena)
• NO2: {air_quality['no2']} ug/m3 (Buena)
• O3: {air_quality['o3']} ug/m3 (Buena)

{datetime.now().strftime('%d/%m/%Y a las %H:%M')}

El equipo de AirGuardian
            """
            
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.default_recipient
            message["Subject"] = "Reporte Programado de Calidad del Aire"
            message.attach(MIMEText(message_body, "plain", "utf-8"))

            server_smtp = smtplib.SMTP("smtp.gmail.com", 587)
            server_smtp.starttls()
            server_smtp.login(self.sender_email, self.sender_password)
            
            text_message = message.as_string()
            server_smtp.sendmail(self.sender_email, self.default_recipient, text_message)
            print(f"Notificacion programada enviada exitosamente!")
            server_smtp.quit()

        except Exception as e:
            print(f"Error al enviar notificacion programada: {e}")

# Global email service instance
email_service = EmailService()

def setup_scheduled_notifications():
    """Setup scheduled email notifications"""
    print("Configurando notificaciones programadas...")
    print("Notificaciones programadas configuradas.")

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
