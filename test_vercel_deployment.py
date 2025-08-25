#!/usr/bin/env python3
"""
Test script to check Vercel deployment status
"""
import requests
import json

def test_vercel_deployment():
    base_url = "https://stock-portfolio-1xqffywiq-tkaldens-projects-4dce0843.vercel.app"
    
    # Test endpoints
    endpoints = [
        "/",
        "/api/health",
        "/api/cache/info"
    ]
    
    print("🔍 Testing Vercel Deployment...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"Response: {response.text[:200]}...")
                else:
                    print(f"Response: {response.text[:200]}...")
            elif response.status_code == 401 or response.status_code == 403:
                print("🔒 Authentication required - deployment protection enabled")
            else:
                print(f"❌ Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_vercel_deployment()
