#!/usr/bin/env python3
import requests
import json
import sys

def test_health_endpoint(port=8001):
    """Test the health endpoint"""
    try:
        url = f'http://127.0.0.1:{port}/health'
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server may not be running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    test_health_endpoint(port)