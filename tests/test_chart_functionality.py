#!/usr/bin/env python3
"""
Test script to verify chart functionality
"""
import requests
import json

def test_chart_endpoints():
    """Test all chart endpoints"""
    base_url = "http://localhost:5001/api"
    
    chart_types = ['value', 'growth', 'dividend']
    
    print("=== Testing Chart Endpoints ===")
    
    for chart_type in chart_types:
        print(f"\nTesting {chart_type} chart:")
        try:
            response = requests.get(f"{base_url}/chart/{chart_type}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    print(f"  ✅ Success! Found {len(data['data'])} sectors")
                    print(f"  Sample sector: {data['data'][0]['title']} with {len(data['data'][0]['labels'])} stocks")
                    print(f"  Sample values: {data['data'][0]['values'][:3]}")
                else:
                    print(f"  ❌ No data returned")
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_cors():
    """Test CORS headers"""
    print("\n=== Testing CORS ===")
    
    try:
        response = requests.get(
            "http://localhost:5001/api/chart/value",
            headers={'Origin': 'http://localhost:3000'}
        )
        
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header == 'http://localhost:3000':
            print("  ✅ CORS properly configured for React app")
        else:
            print(f"  ❌ CORS header: {cors_header}")
            
    except Exception as e:
        print(f"  ❌ CORS test error: {e}")

def test_react_app():
    """Test if React app is accessible"""
    print("\n=== Testing React App ===")
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("  ✅ React app is running on port 3000")
        else:
            print(f"  ❌ React app returned status {response.status_code}")
    except Exception as e:
        print(f"  ❌ React app not accessible: {e}")

if __name__ == "__main__":
    test_chart_endpoints()
    test_cors()
    test_react_app()
    
    print("\n=== Summary ===")
    print("If all tests pass, the chart functionality should be working.")
    print("To access the charts:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Click on 'Charts' in the navigation bar")
    print("3. Or click on 'View Charts' from the home page")
    print("4. You should see tabs for Value, Growth, and Dividend stocks")
    print("5. Each tab should display sector-wise stock analysis") 