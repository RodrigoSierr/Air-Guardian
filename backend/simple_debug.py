#!/usr/bin/env python3
"""
Simple debug script for email functionality
"""

import asyncio
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_smtp_connection():
    """Test basic SMTP connection"""
    print("Testing SMTP connection...")
    
    REMITENTE_EMAIL = "ailingonzales151001@gmail.com"
    REMITENTE_PASS = "ckrutgviyipvbmbp"
    
    try:
        # Test connection
        server = smtplib.SMTP("smtp.gmail.com", 587)
        print("Connected to Gmail SMTP server")
        
        # Test TLS
        server.starttls()
        print("TLS encryption started")
        
        # Test authentication
        server.login(REMITENTE_EMAIL, REMITENTE_PASS)
        print("Authentication successful")
        
        server.quit()
        print("SMTP connection test passed")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Check your email and app password")
        return False
        
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def test_simple_email():
    """Test sending a simple email"""
    print("\nTesting simple email sending...")
    
    REMITENTE_EMAIL = "ailingonzales151001@gmail.com"
    REMITENTE_PASS = "ckrutgviyipvbmbp"
    DESTINATARIO_EMAIL = "yndirasierra@gmail.com"
    
    try:
        # Create simple message
        message = MIMEMultipart()
        message["From"] = REMITENTE_EMAIL
        message["To"] = DESTINATARIO_EMAIL
        message["Subject"] = "Test Email from AirGuardian"
        
        body = "This is a test email from AirGuardian notification system."
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(REMITENTE_EMAIL, REMITENTE_PASS)
        
        text = message.as_string()
        server.sendmail(REMITENTE_EMAIL, DESTINATARIO_EMAIL, text)
        server.quit()
        
        print("Simple email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Error sending simple email: {e}")
        return False

async def test_email_service():
    """Test the full email service"""
    print("\nTesting full email service...")
    
    try:
        from email_service import email_service
        
        test_data = {
            "name": "Test User",
            "email": "yndirasierra@gmail.com",
            "phone": "+1234567890",
            "city": "Lima",
            "location": {"latitude": -12.0464, "longitude": -77.0428}
        }
        
        success = await email_service.send_notification(test_data)
        
        if success:
            print("Email service test passed!")
        else:
            print("Email service test failed!")
            
        return success
        
    except Exception as e:
        print(f"Email service error: {e}")
        return False

async def main():
    """Run all diagnostic tests"""
    print("AirGuardian Email Diagnostic Tool")
    print("=" * 50)
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    if not smtp_ok:
        print("\nSMTP connection failed!")
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Verify Gmail credentials")
        print("3. Enable 'Less secure app access' in Gmail")
        print("4. Use App Password instead of regular password")
        return
    
    # Test simple email
    simple_ok = test_simple_email()
    if not simple_ok:
        print("\nSimple email test failed!")
        return
    
    # Test full service
    service_ok = await test_email_service()
    if not service_ok:
        print("\nEmail service test failed!")
        return
    
    print("\n" + "=" * 50)
    print("All tests passed! Email system is working correctly.")

if __name__ == "__main__":
    asyncio.run(main())
