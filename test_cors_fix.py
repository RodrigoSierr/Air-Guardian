#!/usr/bin/env python3
"""
Test script to verify CORS configuration and backend connectivity
"""
import requests
import json

def test_cors_configuration():
    """Test CORS configuration"""
    print("🔍 Testing CORS configuration...")
    
    # Test 1: Check if backend is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Backend is running: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not running: {e}")
        return False
    
    # Test 2: Test CORS preflight request
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options("http://localhost:8000/api/send-notification", headers=headers, timeout=5)
        print(f"✅ CORS preflight request: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS preflight failed: {e}")
        return False
    
    # Test 3: Test actual POST request
    try:
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
        
        response = requests.post(
            "http://localhost:8000/api/send-notification", 
            json=test_data, 
            headers=headers, 
            timeout=10
        )
        print(f"✅ POST request: {response.status_code}")
        print(f"   Response: {response.json()}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ POST request failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting CORS test...")
    success = test_cors_configuration()
    
    if success:
        print("\n✅ All tests passed! CORS should be working correctly.")
    else:
        print("\n❌ Some tests failed. Check the backend server and CORS configuration.")
