#!/usr/bin/env python3
"""
Test the simple endpoint
"""
import requests

def test_simple_endpoint():
    """Test the simple endpoint"""
    print("Testing simple endpoint...")
    
    try:
        response = requests.post("http://localhost:8000/api/test-simple", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Simple endpoint works!")
            return True
        else:
            print("Simple endpoint failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_endpoint()
