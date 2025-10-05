#!/usr/bin/env python3
"""
Debug script to test the notification endpoint step by step
"""
import sys
import traceback

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    try:
        from fastapi import FastAPI, HTTPException
        print("FastAPI imported")
        
        from pydantic import BaseModel
        print("Pydantic imported")
        
        from email_service_fixed import email_service
        print("Email service imported")
        
        return True
    except Exception as e:
        print(f"Import error: {e}")
        traceback.print_exc()
        return False

def test_email_service():
    """Test email service initialization"""
    print("\nTesting email service...")
    try:
        from email_service_fixed import email_service
        print(f"Email service initialized: {type(email_service)}")
        return True
    except Exception as e:
        print(f"Email service error: {e}")
        traceback.print_exc()
        return False

def test_notification_data():
    """Test notification data structure"""
    print("\nTesting notification data...")
    try:
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "location": {"latitude": -12.0464, "longitude": -77.0428},
            "city": "Lima"
        }
        print(f"Test data created: {test_data}")
        return True
    except Exception as e:
        print(f"Data creation error: {e}")
        traceback.print_exc()
        return False

def test_email_send():
    """Test email sending"""
    print("\nTesting email sending...")
    try:
        from email_service_fixed import email_service
        import asyncio
        
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "location": {"latitude": -12.0464, "longitude": -77.0428},
            "city": "Lima"
        }
        
        # Test the email service
        result = asyncio.run(email_service.send_notification(test_data))
        print(f"Email send result: {result}")
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting debug tests...")
    
    success = True
    success &= test_imports()
    success &= test_email_service()
    success &= test_notification_data()
    success &= test_email_send()
    
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
