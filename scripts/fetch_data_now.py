#!/usr/bin/env python3
"""
Utility script to manually trigger data fetching and cache management
"""
import sys
import os
import logging
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import data_scheduler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def main():
    parser = argparse.ArgumentParser(description='Manual data fetch and cache management')
    parser.add_argument('--force', action='store_true', help='Force refresh all data')
    parser.add_argument('--status', action='store_true', help='Check cache status')
    parser.add_argument('--clear', action='store_true', help='Clear all cached data')
    parser.add_argument('--strength', action='store_true', help='Precalculate strength data only')
    parser.add_argument('--stock', action='store_true', help='Fetch stock data only')
    parser.add_argument('--annual', action='store_true', help='Fetch annual returns only')
    
    args = parser.parse_args()
    
    if args.status:
        print("📊 Checking Cache Status")
        print("=" * 50)
        status = data_scheduler.check_cache_status()
        print(f"Stock Data Entries: {status.get('stock_data', 0)}")
        print(f"Annual Returns Entries: {status.get('annual_returns', 0)}")
        print(f"Strength Data Entries: {status.get('strength_data', 0)}")
        
        if status.get('strength_details'):
            print("\nStrength Data Details:")
            for key, info in status['strength_details'].items():
                print(f"  {key}: {info['expires_in']}")
    
    elif args.clear:
        print("🗑️ Clearing All Cached Data")
        print("=" * 50)
        data_scheduler.clear_all_cache()
        print("✅ All cached data cleared")
    
    elif args.strength:
        print("🧮 Precalculating Strength Data")
        print("=" * 50)
        data_scheduler.precalculate_and_cache_strength_data()
        print("✅ Strength data precalculation completed")
    
    elif args.stock:
        print("📈 Fetching Stock Data")
        print("=" * 50)
        data_scheduler.fetch_and_cache_stock_data()
        print("✅ Stock data fetch completed")
    
    elif args.annual:
        print("📊 Fetching Annual Returns")
        print("=" * 50)
        data_scheduler.fetch_and_cache_annual_returns()
        print("✅ Annual returns fetch completed")
    
    elif args.force:
        print("🔄 Force Refreshing All Data")
        print("=" * 50)
        data_scheduler.daily_data_refresh()
        print("✅ Force refresh completed")
    
    else:
        print("📊 Smart Data Fetch (only if needed)")
        print("=" * 50)
        data_scheduler.fetch_and_cache_stock_data()
        data_scheduler.fetch_and_cache_annual_returns()
        data_scheduler.precalculate_and_cache_strength_data()
        print("✅ Smart data fetch completed")

if __name__ == "__main__":
    main() 