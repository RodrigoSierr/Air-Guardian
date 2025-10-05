#!/usr/bin/env python3
"""
Test script for email functionality
Run this to test the email service independently
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service

async def test_email_service():
    """Test the email service with sample data"""
    print("🧪 Testing Email Service...")
    
    # Test data
    test_user_data = {
        "name": "Usuario de Prueba",
        "email": "test@example.com",  # Change this to your test email
        "phone": "+1234567890",
        "city": "Lima, Perú",
        "location": {"latitude": -12.0464, "longitude": -77.0428}
    }
    
    print(f"📧 Sending test email to: {test_user_data['email']}")
    print(f"📍 Location: {test_user_data['city']}")
    
    try:
        success = await email_service.send_notification(test_user_data)
        
        if success:
            print("✅ Test email sent successfully!")
            print("📬 Check your email inbox for the notification")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    print("🚀 Starting Email Service Test")
    print("=" * 50)
    
    # Run the test
    asyncio.run(test_email_service())
    
    print("=" * 50)
    print("🏁 Test completed")
