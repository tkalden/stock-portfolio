#!/usr/bin/env python3
"""
Yahoo Finance Cache Management Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.annualReturn import AnnualReturn
from utilities.redis_data import redis_manager
import logging
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_cache_status():
    """Display detailed cache status"""
    print("=" * 60)
    print("YAHOO FINANCE CACHE STATUS")
    print("=" * 60)
    
    annual_return = AnnualReturn()
    status = annual_return.get_cache_status()
    
    if status.get('status') == 'cached':
        print(f"✅ Cache Status: {status['status'].upper()}")
        print(f"📊 Records: {status['count']}")
        print(f"⏰ TTL: {status['ttl_human']}")
        print(f"🕐 Created: {status['timestamp']}")
        print(f"📡 Source: {status['source']}")
        print(f"🔢 Version: {status['version']}")
        
        # Check if cache is fresh
        is_fresh = annual_return.is_cache_fresh()
        print(f"🆕 Fresh Cache: {'Yes' if is_fresh else 'No'}")
        
    elif status.get('status') == 'not_cached':
        print("❌ Cache Status: NOT CACHED")
        print("   No Yahoo Finance data found in cache")
        
    elif status.get('status') == 'redis_unavailable':
        print("⚠️  Cache Status: REDIS UNAVAILABLE")
        print("   Redis connection failed")
        
    else:
        print(f"❌ Cache Status: ERROR")
        print(f"   Error: {status.get('error', 'Unknown error')}")

def clear_cache():
    """Clear the Yahoo Finance cache"""
    print("🗑️  Clearing Yahoo Finance cache...")
    annual_return = AnnualReturn()
    annual_return.clear_annual_returns_cache()
    print("✅ Cache cleared successfully")

def refresh_cache():
    """Force refresh of Yahoo Finance data"""
    print("🔄 Forcing refresh of Yahoo Finance data...")
    annual_return = AnnualReturn()
    df = annual_return.force_refresh_annual_returns()
    
    if not df.empty:
        print(f"✅ Successfully refreshed cache with {len(df)} stocks")
        show_cache_status()
    else:
        print("❌ Failed to refresh cache")

def extend_cache(hours):
    """Extend cache TTL"""
    print(f"⏰ Extending cache TTL by {hours} hours...")
    annual_return = AnnualReturn()
    success = annual_return.extend_cache(hours)
    
    if success:
        print(f"✅ Cache TTL extended by {hours} hours")
        show_cache_status()
    else:
        print("❌ Failed to extend cache TTL")

def test_cache_performance():
    """Test cache performance"""
    print("⚡ Testing cache performance...")
    annual_return = AnnualReturn()
    
    import time
    
    # Test cache retrieval
    start_time = time.time()
    df = annual_return.get_annual_return_data()
    cache_time = time.time() - start_time
    
    if not df.empty:
        print(f"✅ Cache retrieval: {cache_time:.3f} seconds")
        print(f"📊 Retrieved {len(df)} stocks from cache")
        
        # Test fresh fetch (if cache is old)
        if not annual_return.is_cache_fresh():
            print("🔄 Testing fresh fetch performance...")
            start_time = time.time()
            fresh_df = annual_return.force_refresh_annual_returns()
            fresh_time = time.time() - start_time
            
            if not fresh_df.empty:
                print(f"✅ Fresh fetch: {fresh_time:.3f} seconds")
                print(f"📊 Retrieved {len(fresh_df)} stocks from Yahoo Finance")
                print(f"🚀 Cache is {fresh_time/cache_time:.1f}x faster than fresh fetch")
            else:
                print("❌ Fresh fetch failed")
        else:
            print("ℹ️  Cache is fresh, skipping fresh fetch test")
    else:
        print("❌ Cache retrieval failed")

def monitor_cache():
    """Monitor cache in real-time"""
    print("👀 Monitoring Yahoo Finance cache...")
    print("Press Ctrl+C to stop")
    
    annual_return = AnnualReturn()
    
    try:
        while True:
            import time
            status = annual_return.get_cache_status()
            
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("=" * 60)
            print("YAHOO FINANCE CACHE MONITOR")
            print("=" * 60)
            print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            if status.get('status') == 'cached':
                print(f"✅ Status: CACHED")
                print(f"📊 Records: {status['count']}")
                print(f"⏰ TTL: {status['ttl_human']}")
                print(f"🆕 Fresh: {'Yes' if annual_return.is_cache_fresh() else 'No'}")
            else:
                print(f"❌ Status: {status.get('status', 'UNKNOWN').upper()}")
            
            print()
            print("Press Ctrl+C to stop monitoring...")
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

def main():
    parser = argparse.ArgumentParser(description='Yahoo Finance Cache Management')
    parser.add_argument('action', choices=['status', 'clear', 'refresh', 'extend', 'test', 'monitor'],
                       help='Action to perform')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours to extend cache TTL (default: 24)')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        show_cache_status()
    elif args.action == 'clear':
        clear_cache()
    elif args.action == 'refresh':
        refresh_cache()
    elif args.action == 'extend':
        extend_cache(args.hours)
    elif args.action == 'test':
        test_cache_performance()
    elif args.action == 'monitor':
        monitor_cache()

if __name__ == "__main__":
    main() 