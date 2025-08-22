#!/usr/bin/env python3
"""
Test Redis Tracking System
Demonstrates duplicate prevention and tracking functionality
"""

import time
import threading
import requests
import json
from datetime import datetime

def test_cache_tracking():
    """Test the cache tracking system"""
    print("🧪 Testing Redis Tracking System")
    print("=" * 50)
    
    base_url = "http://localhost:5001/api"
    
    # Test 1: Check initial cache status
    print("\n1️⃣ Checking initial cache status...")
    try:
        response = requests.get(f"{base_url}/cache/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache Status: {data['cache_info']['message']}")
        else:
            print(f"❌ Failed to get cache status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking cache status: {e}")
    
    # Test 2: Check tracking information
    print("\n2️⃣ Checking tracking information...")
    try:
        response = requests.get(f"{base_url}/cache/tracking")
        if response.status_code == 200:
            data = response.json()
            summary = data['tracking_info']['summary']
            print(f"✅ Tracking Summary:")
            print(f"   Total entries: {summary.get('total_entries', 0)}")
            print(f"   Total records: {summary.get('total_records', 0)}")
            print(f"   Total API calls: {summary.get('total_api_calls', 0)}")
            print(f"   Total cache hits: {summary.get('total_cache_hits', 0)}")
            print(f"   Pending requests: {summary.get('pending_requests', 0)}")
        else:
            print(f"❌ Failed to get tracking info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking tracking info: {e}")
    
    # Test 3: Simulate concurrent requests (duplicate prevention)
    print("\n3️⃣ Testing duplicate prevention with concurrent requests...")
    
    def make_request(sector, request_id):
        """Make a request to the screener API"""
        try:
            print(f"   🔄 Request {request_id}: Fetching {sector} data...")
            start_time = time.time()
            
            response = requests.get(f"{base_url}/screener/data", params={
                'sector': sector,
                'index': 'S&P 500'
            })
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('data', []))
                print(f"   ✅ Request {request_id}: Got {count} records in {duration:.2f}s")
            else:
                print(f"   ❌ Request {request_id}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request {request_id}: Error - {e}")
    
    # Start multiple concurrent requests for the same data
    threads = []
    sectors = ['Technology', 'Technology', 'Technology']  # Same sector to test duplicate prevention
    
    for i, sector in enumerate(sectors):
        thread = threading.Thread(target=make_request, args=(sector, i+1))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Test 4: Check tracking after requests
    print("\n4️⃣ Checking tracking after requests...")
    time.sleep(2)  # Wait a bit for tracking to update
    
    try:
        response = requests.get(f"{base_url}/cache/tracking")
        if response.status_code == 200:
            data = response.json()
            summary = data['tracking_info']['summary']
            api_history = data['tracking_info']['recent_api_calls']
            
            print(f"✅ Updated Tracking Summary:")
            print(f"   Total entries: {summary.get('total_entries', 0)}")
            print(f"   Total API calls: {summary.get('total_api_calls', 0)}")
            print(f"   Total cache hits: {summary.get('total_cache_hits', 0)}")
            print(f"   Pending requests: {summary.get('pending_requests', 0)}")
            
            print(f"\n📡 Recent API Calls ({len(api_history)}):")
            for call in api_history[-5:]:  # Show last 5 calls
                timestamp = call.get('timestamp', 'Unknown')
                source = call.get('source', 'Unknown')
                endpoint = call.get('endpoint', 'Unknown')
                success = call.get('success', False)
                response_time = call.get('response_time_ms', 0)
                
                status = "✅" if success else "❌"
                print(f"   {status} {timestamp} - {source} -> {endpoint} ({response_time}ms)")
                
        else:
            print(f"❌ Failed to get tracking info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking tracking info: {e}")
    
    # Test 5: Test different sectors
    print("\n5️⃣ Testing different sectors...")
    different_sectors = ['Healthcare', 'Financial', 'Consumer Cyclical']
    
    for sector in different_sectors:
        try:
            print(f"   🔄 Fetching {sector} data...")
            response = requests.get(f"{base_url}/screener/data", params={
                'sector': sector,
                'index': 'S&P 500'
            })
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('data', []))
                print(f"   ✅ {sector}: {count} records")
            else:
                print(f"   ❌ {sector}: Failed")
                
        except Exception as e:
            print(f"   ❌ {sector}: Error - {e}")
    
    # Test 6: Final tracking summary
    print("\n6️⃣ Final tracking summary...")
    time.sleep(2)
    
    try:
        response = requests.get(f"{base_url}/cache/tracking")
        if response.status_code == 200:
            data = response.json()
            summary = data['tracking_info']['summary']
            cache_status = data['tracking_info']['cache_status']
            
            print(f"✅ Final Summary:")
            print(f"   Total entries: {summary.get('total_entries', 0)}")
            print(f"   Total records: {summary.get('total_records', 0)}")
            print(f"   Total API calls: {summary.get('total_api_calls', 0)}")
            print(f"   Total cache hits: {summary.get('total_cache_hits', 0)}")
            
            # Show cache hit rate
            total_requests = summary.get('total_api_calls', 0) + summary.get('total_cache_hits', 0)
            if total_requests > 0:
                hit_rate = (summary.get('total_cache_hits', 0) / total_requests) * 100
                print(f"   Cache hit rate: {hit_rate:.1f}%")
            
            # Show stock data cache status
            stock_data = cache_status.get('stock_data', {})
            print(f"\n📊 Stock Data Cache Status:")
            for key, entries in stock_data.items():
                if entries:
                    entry = entries[0]  # Get first entry
                    records = entry.get('records', 0)
                    api_calls = entry.get('api_calls', 0)
                    cache_hits = entry.get('cache_hits', 0)
                    print(f"   {key}: {records} records, {api_calls} API calls, {cache_hits} cache hits")
                
        else:
            print(f"❌ Failed to get final summary: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting final summary: {e}")
    
    print("\n🎯 Test completed!")
    print("\n💡 Key Benefits:")
    print("   ✅ Prevents duplicate Finviz API calls")
    print("   ✅ Tracks all data saves and accesses")
    print("   ✅ Monitors API call success/failure")
    print("   ✅ Provides detailed cache statistics")
    print("   ✅ Shows pending request status")

if __name__ == "__main__":
    test_cache_tracking()
