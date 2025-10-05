#!/usr/bin/env python3
"""
Test script to debug the notification endpoint
"""
import requests
import json

def test_notification_endpoint():
    """Test the notification endpoint directly"""
    print("Testing notification endpoint...")
    
    test_data = {
        "name": "Test User",
        "phone": "+1234567890",
        "email": "test@example.com",
        "location": {"latitude": -12.0464, "longitude": -77.0428},
        "city": "Lima"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5173'
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/send-notification", 
            json=test_data, 
            headers=headers, 
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print("Notification failed")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_notification_endpoint()
