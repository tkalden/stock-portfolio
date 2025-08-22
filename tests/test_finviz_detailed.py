#!/usr/bin/env python3
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

def test_finviz_direct():
    print("=== Testing Finviz Direct Web Scraping ===")
    
    # Test 1: Direct web scraping of Finviz
    print("\n1. Testing Finviz web scraping for AAPL:")
    try:
        url = "https://finviz.com/quote.ashx?t=AAPL"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the snapshot table
            snapshot_table = soup.find('table', {'class': 'snapshot-table2'})
            if snapshot_table:
                rows = snapshot_table.find_all('tr')
                data = {}
                for row in rows:
                    cells = row.find_all('td')
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            key = cells[i].get_text(strip=True)
                            value = cells[i + 1].get_text(strip=True)
                            data[key] = value
                
                print(f"   ✅ Success! Found {len(data)} data points")
                print(f"   Price: ${data.get('Price', 'N/A')}")
                print(f"   Market Cap: {data.get('Market Cap', 'N/A')}")
                print(f"   P/E: {data.get('P/E', 'N/A')}")
                print(f"   Volume: {data.get('Volume', 'N/A')}")
            else:
                print("   ❌ Could not find snapshot table")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Finviz screener
    print("\n2. Testing Finviz screener for S&P 500:")
    try:
        url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the screener table
            table = soup.find('table', {'class': 'table-light'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                tickers = []
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        ticker = cells[1].get_text(strip=True)
                        tickers.append(ticker)
                
                print(f"   ✅ Success! Found {len(tickers)} S&P 500 stocks")
                print(f"   Sample tickers: {tickers[:10]}")
            else:
                print("   ❌ Could not find screener table")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_finvizfinance_library():
    print("\n=== Testing FinvizFinance Library ===")
    
    try:
        from finvizfinance.quote import finvizfinance
        print("\n1. Testing FinvizFinance single stock:")
        
        stock = finvizfinance('AAPL')
        stock_fundament = stock.ticker_fundament()
        
        if stock_fundament:
            print(f"   ✅ Success! Found fundamental data")
            print(f"   Price: ${stock_fundament.get('Price', 'N/A')}")
            print(f"   Market Cap: {stock_fundament.get('Market Cap', 'N/A')}")
            print(f"   P/E: {stock_fundament.get('P/E', 'N/A')}")
            print(f"   Available fields: {list(stock_fundament.keys())}")
        else:
            print("   ❌ No fundamental data returned")
            
    except Exception as e:
        print(f"   ❌ FinvizFinance Error: {e}")
    
    try:
        from finvizfinance.screener.overview import Overview
        print("\n2. Testing FinvizFinance screener:")
        
        foverview = Overview()
        filters_dict = {'Market Cap.': '+Mid (over $2bln)'}
        foverview.set_filter(filters_dict=filters_dict)
        df = foverview.screener_view()
        
        if not df.empty:
            print(f"   ✅ Success! Found {len(df)} stocks")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Sample tickers: {list(df['Ticker'].head(5))}")
        else:
            print("   ❌ No screener data returned")
            
    except Exception as e:
        print(f"   ❌ FinvizFinance Screener Error: {e}")

def compare_data_sources():
    print("\n=== Comparing Data Sources ===")
    
    # Test Yahoo Finance
    print("\n1. Yahoo Finance data for AAPL:")
    try:
        import yfinance as yf
        ticker = yf.Ticker('AAPL')
        info = ticker.info
        hist = ticker.history(period='1d')
        
        print(f"   Price: ${hist['Close'].iloc[-1]:.2f}")
        print(f"   Market Cap: ${info.get('marketCap', 0):,}")
        print(f"   P/E: {info.get('trailingPE', 'N/A')}")
        print(f"   Volume: {hist['Volume'].iloc[-1]:,}")
        
    except Exception as e:
        print(f"   ❌ Yahoo Finance Error: {e}")
    
    # Test Finviz direct scraping
    print("\n2. Finviz direct scraping for AAPL:")
    try:
        url = "https://finviz.com/quote.ashx?t=AAPL"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            snapshot_table = soup.find('table', {'class': 'snapshot-table2'})
            
            if snapshot_table:
                rows = snapshot_table.find_all('tr')
                data = {}
                for row in rows:
                    cells = row.find_all('td')
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            key = cells[i].get_text(strip=True)
                            value = cells[i + 1].get_text(strip=True)
                            data[key] = value
                
                print(f"   Price: ${data.get('Price', 'N/A')}")
                print(f"   Market Cap: {data.get('Market Cap', 'N/A')}")
                print(f"   P/E: {data.get('P/E', 'N/A')}")
                print(f"   Volume: {data.get('Volume', 'N/A')}")
            else:
                print("   ❌ Could not find data table")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Finviz Error: {e}")

if __name__ == "__main__":
    test_finviz_direct()
    test_finvizfinance_library()
    compare_data_sources() 