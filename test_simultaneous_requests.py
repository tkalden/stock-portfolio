#!/usr/bin/env python3
"""
Test Simultaneous Requests
Simulates multiple concurrent requests to test duplicate prevention
"""

import time
import threading
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_screener_request(request_id, sector="Real Estate", index="S&P 500"):
    """Make a request to the screener API"""
    start_time = time.time()
    
    try:
        print(f"🔄 Request {request_id}: Starting request for {sector}...")
        
        response = requests.get("http://localhost:5001/api/screener/data", params={
            'sector': sector,
            'index': index
        }, timeout=30)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('data', []))
            print(f"✅ Request {request_id}: Success! Got {count} records in {duration:.2f}s")
            return {
                'request_id': request_id,
                'success': True,
                'duration': duration,
                'record_count': count,
                'status_code': response.status_code
            }
        else:
            print(f"❌ Request {request_id}: Failed with status {response.status_code} in {duration:.2f}s")
            return {
                'request_id': request_id,
                'success': False,
                'duration': duration,
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"⏰ Request {request_id}: Timeout after {duration:.2f}s")
        return {
            'request_id': request_id,
            'success': False,
            'duration': duration,
            'error': 'Timeout'
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Request {request_id}: Error - {e} in {duration:.2f}s")
        return {
            'request_id': request_id,
            'success': False,
            'duration': duration,
            'error': str(e)
        }

def test_simultaneous_requests():
    """Test simultaneous requests to the screener"""
    print("🧪 Testing Simultaneous Requests for Real Estate")
    print("=" * 60)
    
    # Check if the server is running
    try:
        health_response = requests.get("http://localhost:5001/api/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running on http://localhost:5001")
        return
    
    print("✅ Server is running")
    
    # Test parameters
    sector = "Real Estate"
    index = "S&P 500"
    num_requests = 5  # Number of simultaneous requests
    
    print(f"\n🎯 Making {num_requests} simultaneous requests for {sector} sector...")
    print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    # Create requests with slight delays to ensure they're truly simultaneous
    requests_list = []
    for i in range(num_requests):
        requests_list.append((i + 1, sector, index))
    
    # Execute requests simultaneously
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        # Submit all requests
        future_to_request = {
            executor.submit(make_screener_request, req_id, req_sector, req_index): req_id 
            for req_id, req_sector, req_index in requests_list
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_request):
            result = future.result()
            results.append(result)
    
    total_duration = time.time() - start_time
    
    # Analyze results
    print(f"\n📊 Results Summary:")
    print(f"⏰ Total duration: {total_duration:.2f}s")
    print(f"📈 Average duration per request: {total_duration/num_requests:.2f}s")
    
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    
    print(f"✅ Successful requests: {len(successful_requests)}/{num_requests}")
    print(f"❌ Failed requests: {len(failed_requests)}/{num_requests}")
    
    if successful_requests:
        durations = [r['duration'] for r in successful_requests]
        record_counts = [r['record_count'] for r in successful_requests]
        
        print(f"⏱️  Fastest request: {min(durations):.2f}s")
        print(f"⏱️  Slowest request: {max(durations):.2f}s")
        print(f"📊 Average records per request: {sum(record_counts)/len(record_counts):.1f}")
        
        # Check for consistency
        unique_record_counts = set(record_counts)
        if len(unique_record_counts) == 1:
            print(f"✅ All requests returned same number of records: {record_counts[0]}")
        else:
            print(f"⚠️  Inconsistent record counts: {unique_record_counts}")
    
    if failed_requests:
        print(f"\n❌ Failed Requests:")
        for result in failed_requests:
            print(f"   Request {result['request_id']}: {result.get('error', 'Unknown error')}")
    
    # Check tracking information
    print(f"\n🔍 Checking tracking information...")
    try:
        tracking_response = requests.get("http://localhost:5001/api/cache/tracking", timeout=5)
        if tracking_response.status_code == 200:
            tracking_data = tracking_response.json()
            summary = tracking_data['tracking_info']['summary']
            
            print(f"📊 Tracking Summary:")
            print(f"   Total API calls: {summary.get('total_api_calls', 0)}")
            print(f"   Total cache hits: {summary.get('total_cache_hits', 0)}")
            print(f"   Pending requests: {summary.get('pending_requests', 0)}")
            
            # Calculate cache hit rate
            total_requests = summary.get('total_api_calls', 0) + summary.get('total_cache_hits', 0)
            if total_requests > 0:
                hit_rate = (summary.get('total_cache_hits', 0) / total_requests) * 100
                print(f"   Cache hit rate: {hit_rate:.1f}%")
            
            # Show recent API calls
            api_history = tracking_data['tracking_info']['recent_api_calls']
            if api_history:
                print(f"\n📡 Recent API Calls:")
                for call in api_history[-3:]:  # Show last 3 calls
                    timestamp = call.get('timestamp', 'Unknown')
                    source = call.get('source', 'Unknown')
                    endpoint = call.get('endpoint', 'Unknown')
                    success = call.get('success', False)
                    response_time = call.get('response_time_ms', 0)
                    
                    status = "✅" if success else "❌"
                    print(f"   {status} {timestamp} - {source} -> {endpoint} ({response_time}ms)")
        else:
            print(f"❌ Failed to get tracking info: {tracking_response.status_code}")
    except Exception as e:
        print(f"❌ Error getting tracking info: {e}")
    
    # Check specific cache status for Real Estate
    print(f"\n🏠 Real Estate Cache Status:")
    try:
        cache_key = f"stock_data:{index}:{sector}"
        cache_response = requests.get("http://localhost:5001/api/cache/info", timeout=5)
        if cache_response.status_code == 200:
            cache_data = cache_response.json()
            cache_info = cache_data['cache_info']
            print(f"   Cache working: {cache_info['message']}")
            print(f"   Memory usage: {cache_info['memory_usage']}")
        else:
            print(f"   ❌ Failed to get cache info: {cache_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting cache info: {e}")
    
    print(f"\n🎯 Test completed at: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    # Summary
    print(f"\n💡 Expected Behavior:")
    print(f"   ✅ Only 1 Finviz API call should be made")
    print(f"   ✅ Other requests should use cached data")
    print(f"   ✅ All requests should return same data")
    print(f"   ✅ Cache hit rate should be high")

if __name__ == "__main__":
    test_simultaneous_requests()
