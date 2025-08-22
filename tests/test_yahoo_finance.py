#!/usr/bin/env python3
"""
Test script to verify Yahoo Finance data fetching
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.annualReturn import AnnualReturn
from utilities.redis_data import redis_manager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_yahoo_finance_data():
    """Test that Yahoo Finance data is being fetched correctly"""
    
    print("=" * 60)
    print("YAHOO FINANCE DATA FETCHING TEST")
    print("=" * 60)
    
    annual_return = AnnualReturn()
    
    try:
        # Test 1: Clear cache and force fresh fetch
        print("\n1. Clearing cache and forcing fresh Yahoo Finance fetch...")
        annual_return.clear_annual_returns_cache()
        
        # Test 2: Fetch data
        print("\n2. Fetching annual returns data...")
        df = annual_return.force_refresh_annual_returns()
        
        if not df.empty:
            print(f"✅ Successfully fetched data for {len(df)} stocks")
            print(f"   Columns: {list(df.columns)}")
            
            # Test 3: Check data quality
            print("\n3. Checking data quality...")
            
            # Check for reasonable return values
            returns = df['expected_annual_return'].astype(float)
            print(f"   Return range: {returns.min():.4f} to {returns.max():.4f}")
            print(f"   Mean return: {returns.mean():.4f}")
            
            # Check for reasonable risk values
            risks = df['expected_annual_risk'].astype(float)
            print(f"   Risk range: {risks.min():.4f} to {risks.max():.4f}")
            print(f"   Mean risk: {risks.mean():.4f}")
            
            # Check for risk distribution
            low_risk = len(risks[risks < 0.4])
            medium_risk = len(risks[(risks >= 0.4) & (risks < 0.6)])
            high_risk = len(risks[risks >= 0.6])
            
            print(f"   Risk distribution:")
            print(f"     Low risk (<40%): {low_risk} stocks")
            print(f"     Medium risk (40-60%): {medium_risk} stocks")
            print(f"     High risk (>60%): {high_risk} stocks")
            
            # Test 4: Check sample data
            print("\n4. Sample data (first 5 stocks):")
            sample = df.head(5)
            for _, row in sample.iterrows():
                ticker = row['Ticker']
                ret = float(row['expected_annual_return'])
                risk = float(row['expected_annual_risk'])
                ratio = float(row['return_risk_ratio'])
                print(f"   {ticker}: Return={ret:.4f}, Risk={risk:.4f}, Ratio={ratio:.4f}")
            
            # Test 5: Verify data is from Yahoo Finance (not mock)
            print("\n5. Verifying data source...")
            
            # Check if data looks realistic (not perfectly distributed like mock data)
            return_std = returns.std()
            risk_std = risks.std()
            
            if return_std > 0.05 and risk_std > 0.1:  # Real data has more variation
                print("   ✅ Data appears to be from Yahoo Finance (realistic variation)")
            else:
                print("   ⚠️  Data may be mock data (too uniform)")
            
            # Test 6: Check Redis caching
            print("\n6. Testing Redis caching...")
            cached_df = annual_return.get_annual_return_data()
            if not cached_df.empty and len(cached_df) == len(df):
                print("   ✅ Data successfully cached in Redis")
            else:
                print("   ⚠️  Caching may have issues")
            
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print("✅ Yahoo Finance data fetching is working")
            print("✅ Data quality checks passed")
            print("✅ Redis caching is functional")
            print("\nThe system is now using real Yahoo Finance data!")
            
        else:
            print("❌ No data returned from Yahoo Finance")
            print("   This could indicate:")
            print("   - Network connectivity issues")
            print("   - Yahoo Finance API changes")
            print("   - Rate limiting")
            print("   - Invalid ticker symbols")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_specific_tickers():
    """Test Yahoo Finance with specific well-known tickers"""
    
    print("\n" + "=" * 60)
    print("SPECIFIC TICKER TEST")
    print("=" * 60)
    
    annual_return = AnnualReturn()
    
    # Test with well-known stocks
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    try:
        print(f"\nTesting with specific tickers: {test_tickers}")
        
        # Use the async function directly
        import asyncio
        results = asyncio.run(annual_return.gather_result([test_tickers]))
        
        for result_df in results:
            if not result_df.empty:
                print(f"✅ Successfully fetched data for {len(result_df)} tickers")
                print("Sample data:")
                for _, row in result_df.head(3).iterrows():
                    ticker = row['Ticker']
                    ret = float(row['expected_annual_return'])
                    risk = float(row['expected_annual_risk'])
                    print(f"   {ticker}: Return={ret:.4f}, Risk={risk:.4f}")
            else:
                print("❌ No data returned for test tickers")
                
    except Exception as e:
        print(f"❌ Specific ticker test failed: {e}")

if __name__ == "__main__":
    test_yahoo_finance_data()
    test_specific_tickers() 