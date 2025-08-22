#!/usr/bin/env python3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def test_yahoo_finance():
    print("=== Testing Yahoo Finance API Directly ===")
    
    # Test 1: Single ticker
    print("\n1. Testing single ticker (AAPL):")
    try:
        ticker = yf.Ticker('AAPL')
        hist = ticker.history(period='1y')
        print(f"   ✅ Success! Data shape: {hist.shape}")
        print(f"   Latest price: ${hist['Close'].iloc[-1]:.2f}")
        print(f"   Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
        print(f"   Columns: {list(hist.columns)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Multiple tickers
    print("\n2. Testing multiple tickers (AAPL, MSFT, GOOGL):")
    try:
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        data = yf.download(tickers, period='1y', group_by='ticker')
        print(f"   ✅ Success! Data shape: {data.shape}")
        print(f"   Columns: {list(data.columns)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Specific date range
    print("\n3. Testing specific date range (last 2 years):")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        hist = yf.download('AAPL', start=start_date, end=end_date)
        print(f"   ✅ Success! Data shape: {hist.shape}")
        print(f"   Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Problematic ticker from logs
    print("\n4. Testing problematic ticker (GEV):")
    try:
        ticker = yf.Ticker('GEV')
        hist = ticker.history(period='1y')
        print(f"   ✅ Success! Data shape: {hist.shape}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Check if ticker exists
    print("\n5. Testing ticker info:")
    try:
        ticker = yf.Ticker('AAPL')
        info = ticker.info
        print(f"   ✅ Success! Company: {info.get('longName', 'N/A')}")
        print(f"   Sector: {info.get('sector', 'N/A')}")
        print(f"   Market Cap: ${info.get('marketCap', 0):,}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_finviz_alternative():
    print("\n=== Testing Finviz Alternative ===")
    
    try:
        from finvizfinance.quote import finvizfinance
        print("\n1. Testing Finviz single stock:")
        stock = finvizfinance('AAPL')
        stock_fundament = stock.ticker_fundament()
        print(f"   ✅ Success! Price: ${stock_fundament['Price']}")
        print(f"   Market Cap: ${stock_fundament['Market Cap']}")
        print(f"   P/E: {stock_fundament['P/E']}")
        
        print("\n2. Testing Finviz screener:")
        from finvizfinance.screener.overview import Overview
        foverview = Overview()
        filters_dict = {'Market Cap.': '+Mid (over $2bln)', 'Sector': 'Technology'}
        foverview.set_filter(filters_dict=filters_dict)
        df = foverview.screener_view()
        print(f"   ✅ Success! Found {len(df)} technology stocks")
        print(f"   Sample tickers: {list(df['Ticker'].head(5))}")
        
    except Exception as e:
        print(f"   ❌ Finviz Error: {e}")

if __name__ == "__main__":
    test_yahoo_finance()
    test_finviz_alternative() 