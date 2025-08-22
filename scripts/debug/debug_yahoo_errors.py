#!/usr/bin/env python3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import asyncio

def debug_yahoo_errors():
    print("=== Debugging Yahoo Finance Errors ===")
    
    # Test the exact same parameters from our application
    print("\n1. Testing with exact application parameters:")
    try:
        # This is the exact date range from our logs
        start_date = datetime(2018, 1, 1)
        end_date = datetime(2024, 1, 1)
        
        print(f"   Date range: {start_date.date()} to {end_date.date()}")
        
        # Test with problematic ticker
        ticker = 'GEV'
        print(f"   Testing ticker: {ticker}")
        
        # Method 1: Using yf.download (what our app uses)
        print("   Method 1: yf.download")
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            print(f"   ✅ Success! Shape: {data.shape}")
            print(f"   Columns: {list(data.columns)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Method 2: Using Ticker object
        print("   Method 2: Ticker object")
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(start=start_date, end=end_date)
            print(f"   ✅ Success! Shape: {hist.shape}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Method 3: Check if ticker exists
        print("   Method 3: Ticker info")
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            print(f"   ✅ Success! Company: {info.get('longName', 'N/A')}")
            print(f"   Sector: {info.get('sector', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
    except Exception as e:
        print(f"   ❌ General Error: {e}")
    
    # Test with working tickers
    print("\n2. Testing with working tickers (AAPL, MSFT):")
    working_tickers = ['AAPL', 'MSFT']
    
    for ticker in working_tickers:
        print(f"   Testing {ticker}:")
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            print(f"   ✅ Success! Shape: {data.shape}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test chunking (like our app does)
    print("\n3. Testing chunking approach:")
    try:
        # Simulate our app's chunking
        all_tickers = ['AAPL', 'MSFT', 'GOOGL', 'GEV', 'SOLV']
        chunk_size = 50
        
        for i in range(0, len(all_tickers), chunk_size):
            chunk = all_tickers[i:i+chunk_size]
            print(f"   Processing chunk {i//chunk_size + 1}: {chunk}")
            
            try:
                data = yf.download(chunk, start=start_date, end=end_date, group_by='ticker')
                print(f"   ✅ Success! Shape: {data.shape}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"   ❌ Chunking Error: {e}")

def test_alternative_approaches():
    print("\n=== Testing Alternative Approaches ===")
    
    # Test with shorter date range
    print("\n1. Testing with shorter date range (1 year):")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        ticker = 'GEV'
        data = yf.download(ticker, start=start_date, end=end_date)
        print(f"   ✅ Success! Shape: {data.shape}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with different period parameter
    print("\n2. Testing with period parameter:")
    try:
        ticker = 'GEV'
        data = yf.download(ticker, period='1y')
        print(f"   ✅ Success! Shape: {data.shape}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with auto_adjust parameter
    print("\n3. Testing with auto_adjust=False:")
    try:
        ticker = 'GEV'
        data = yf.download(ticker, period='1y', auto_adjust=False)
        print(f"   ✅ Success! Shape: {data.shape}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_problematic_tickers():
    print("\n=== Checking Problematic Tickers ===")
    
    problematic_tickers = ['GEV', 'SOLV']
    
    for ticker in problematic_tickers:
        print(f"\nChecking {ticker}:")
        
        # Check if ticker exists
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            if info:
                print(f"   ✅ Ticker exists")
                print(f"   Company: {info.get('longName', 'N/A')}")
                print(f"   Sector: {info.get('sector', 'N/A')}")
                print(f"   Market Cap: {info.get('marketCap', 'N/A')}")
                
                # Check if it's delisted
                if info.get('marketCap') is None or info.get('marketCap') == 0:
                    print(f"   ⚠️  Possibly delisted (no market cap)")
                    
            else:
                print(f"   ❌ No info available")
                
        except Exception as e:
            print(f"   ❌ Error getting info: {e}")
        
        # Try to get recent data
        try:
            data = yf.download(ticker, period='1mo')
            if not data.empty:
                print(f"   ✅ Recent data available: {data.shape}")
            else:
                print(f"   ❌ No recent data")
        except Exception as e:
            print(f"   ❌ Error getting recent data: {e}")

if __name__ == "__main__":
    debug_yahoo_errors()
    test_alternative_approaches()
    check_problematic_tickers() 