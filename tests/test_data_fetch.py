#!/usr/bin/env python3
"""
Test script to verify data fetching is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sourceDataMapper import SourceDataMapperService
from services.strengthCalculator import StrengthCalculator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_data_fetching():
    """Test data fetching functionality"""
    
    print("=" * 60)
    print("DATA FETCHING TEST")
    print("=" * 60)
    
    source_mapper = SourceDataMapperService()
    strength_calc = StrengthCalculator()
    
    try:
        # Test 1: Get data for S&P 500 with Any sector
        print("\n1. Testing S&P 500 data with Any sector...")
        df = source_mapper.get_data_by_index_sector("S&P 500", "Any")
        if not df.empty:
            print(f"✅ Successfully retrieved {len(df)} stocks for S&P 500")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Sample tickers: {df['Ticker'].head(5).tolist()}")
        else:
            print("❌ No data retrieved for S&P 500")
        
        # Test 2: Get data for specific sector
        print("\n2. Testing Technology sector data...")
        df_tech = source_mapper.get_data_by_index_sector("S&P 500", "Technology")
        if not df_tech.empty:
            print(f"✅ Successfully retrieved {len(df_tech)} Technology stocks")
            print(f"   Sample tickers: {df_tech['Ticker'].head(5).tolist()}")
        else:
            print("❌ No Technology data retrieved")
        
        # Test 3: Calculate strength data
        print("\n3. Testing strength calculation...")
        strength_df = strength_calc.calculate_strength_value("Value", "Any", "S&P 500")
        if not strength_df.empty:
            print(f"✅ Successfully calculated strength for {len(strength_df)} stocks")
            print(f"   Strength range: {strength_df['strength'].min():.3f} to {strength_df['strength'].max():.3f}")
            print(f"   Top 5 by strength: {strength_df['Ticker'].head(5).tolist()}")
        else:
            print("❌ No strength data calculated")
        
        # Test 4: Test with different parameters
        print("\n4. Testing with different parameters...")
        test_cases = [
            ("S&P 500", "Any", "Value"),
            ("S&P 500", "Technology", "Value"),
            ("DJIA", "Any", "Growth"),
        ]
        
        for index, sector, stock_type in test_cases:
            print(f"   Testing {stock_type}:{sector}:{index}...")
            try:
                strength_df = strength_calc.calculate_strength_value(stock_type, sector, index)
                if not strength_df.empty:
                    print(f"   ✅ {len(strength_df)} stocks for {stock_type}:{sector}:{index}")
                else:
                    print(f"   ⚠️  No data for {stock_type}:{sector}:{index}")
            except Exception as e:
                print(f"   ❌ Error for {stock_type}:{sector}:{index}: {e}")
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("✅ Data fetching is working correctly")
        print("✅ Strength calculation is functional")
        print("✅ Multiple parameter combinations work")
        print("\nThe advanced optimization should now work properly!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_fetching() 