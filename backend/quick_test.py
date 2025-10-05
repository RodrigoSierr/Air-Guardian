#!/usr/bin/env python3
"""
Quick test for email functionality
Run this to quickly test if email sending works
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    """Quick test of email functionality"""
    print("🚀 Quick Email Test")
    print("=" * 30)
    
    try:
        from email_service import email_service
        
        # Test data
        test_data = {
            "name": "Test User",
            "email": "yndirasierra@gmail.com",  # Change to your email
            "phone": "+1234567890",
            "city": "Lima",
            "location": {"latitude": -12.0464, "longitude": -77.0428}
        }
        
        print(f"📧 Testing with email: {test_data['email']}")
        print("⏳ Sending test email...")
        
        success = await email_service.send_notification(test_data)
        
        if success:
            print("✅ SUCCESS! Email sent successfully!")
            print("📬 Check your email inbox")
        else:
            print("❌ FAILED! Email could not be sent")
            print("💡 Check the error messages above")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("💡 Make sure the backend is running and all dependencies are installed")

if __name__ == "__main__":
    asyncio.run(quick_test())
