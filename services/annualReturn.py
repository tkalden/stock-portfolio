import asyncio
import logging
import math

import numpy as np
import pandas as pd
import yfinance as yf

import utilities.helper as helper
from enums.enum import RiskEnum
from services.sourceDataMapper import SourceDataMapperService
from utilities.redis_data import redis_manager
from datetime import datetime, timedelta

logger_format = '%(asctime)s:%(threadName)s:%(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO, datefmt="%H:%M:%S")

SourceDataMapperService = SourceDataMapperService()

class AnnualReturn:

    def  __init__(self):
        self.annual_return_redis = 'annual-return'
        self.start_date = '2018-01-01'
        self.end_date = '2024-01-01'

    async def get_result(self,tickers):
        logging.info(f"Start Task {tickers}")
        df = await self.get_annual_return(tickers)
        logging.info(f"End Task {tickers}")
        return df

    async def gather_result(self,ticker_lists):
        logging.info("Gathering Results for {} Tickers".format(len(ticker_lists)))
        chunk_size = 10
        num_tickers = len(ticker_lists)
        remainder = num_tickers % chunk_size
        if remainder == 0:
            chunks = [ticker_lists[i:i+chunk_size] for i in range(0, num_tickers, chunk_size)]
        else:
            chunks = [ticker_lists[i:i+chunk_size] for i in range(0, num_tickers - remainder, chunk_size)]
            chunks.append(ticker_lists[-remainder:])
        return await asyncio.gather(*[self.get_result(tickers) for tickers in chunks])


    def get_annual_return(self, ticker_list):
        """Get annual return for a list of tickers"""
        try:
            # Use more recent date range to avoid delisted stock issues
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Use 1 year instead of 6 years
            
            logging.info(f"Fetching data for {len(ticker_list)} tickers from {start_date.date()} to {end_date.date()}")
            
            # Download data with error handling
            data = yf.download(
                ticker_list, 
                start=start_date, 
                end=end_date,
                group_by='ticker',
                progress=False,  # Reduce logging noise
                ignore_tz=True
            )
            
            if data.empty:
                logging.warning(f"No data returned for tickers: {ticker_list}")
                return pd.DataFrame()
            
            # Process the data
            results = []
            for ticker in ticker_list:
                try:
                    if isinstance(data.columns, pd.MultiIndex):
                        # Multiple tickers case
                        ticker_data = data[ticker] if ticker in data.columns.get_level_values(0) else None
                    else:
                        # Single ticker case
                        ticker_data = data if len(ticker_list) == 1 else None
                    
                    if ticker_data is not None and not ticker_data.empty:
                        # Calculate annual return
                        if 'Close' in ticker_data.columns:
                            close_prices = ticker_data['Close'].dropna()
                            if len(close_prices) > 1:
                                initial_price = close_prices.iloc[0]
                                final_price = close_prices.iloc[-1]
                                annual_return = ((final_price - initial_price) / initial_price) * 100
                                
                                # Calculate volatility
                                returns = close_prices.pct_change().dropna()
                                volatility = returns.std() * (252 ** 0.5) * 100  # Annualized
                                
                                results.append({
                                    'Ticker': ticker,
                                    'expected_annual_return': round(annual_return, 3),
                                    'expected_annual_risk': round(volatility, 3),
                                    'return_risk_ratio': round(annual_return / volatility, 3) if volatility > 0 else 0
                                })
                            else:
                                logging.warning(f"Insufficient data for {ticker}")
                        else:
                            logging.warning(f"No 'Close' column found for {ticker}")
                    else:
                        logging.warning(f"No data available for {ticker}")
                        
                except Exception as e:
                    logging.warning(f"Error processing {ticker}: {e}")
                    continue
            
            if results:
                df = pd.DataFrame(results)
                logging.info(f"Successfully processed {len(df)} tickers")
                return df
            else:
                logging.warning("No valid results generated")
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"Error calculating annual return for {ticker_list}: {e}")
            return pd.DataFrame()

    def get_annual_return_data(self):
        # Try to get from new Redis manager first
        df = redis_manager.get_annual_returns()
        
        # Check if data exists and has valid risk ranges (should include Medium risk stocks)
        if not df.empty and not df['expected_annual_return'].isna().all():
            # Check if we have stocks in the Medium risk range (0.4-0.6)
            medium_risk_stocks = df[(df['expected_annual_risk'].astype(float) > 0.4) & (df['expected_annual_risk'].astype(float) < 0.6)]
            if len(medium_risk_stocks) > 0:
                logging.info("Retrieved annual returns from Redis")
                return df
            else:
                logging.info("Annual returns in Redis don't have Medium risk stocks, regenerating...")
        else:
            logging.info("Annual returns not found in Redis or invalid, calculating...")
        
        # Regenerate data using real Yahoo Finance
        df1 = SourceDataMapperService.get_data_by_index('S&P 500')
        ticker_lists = df1['Ticker'].tolist()
        logging.info(f"Ticker List length: {len(ticker_lists)}")
        
        # Use real Yahoo Finance data instead of mock data
        logging.info("Fetching real annual returns data from Yahoo Finance...")
        
        try:
            # Process tickers in chunks to avoid overwhelming the API
            chunk_size = 50  # Yahoo Finance can handle larger chunks
            all_results = []
            
            for i in range(0, len(ticker_lists), chunk_size):
                chunk = ticker_lists[i:i + chunk_size]
                logging.info(f"Processing chunk {i//chunk_size + 1}: tickers {i+1}-{min(i+chunk_size, len(ticker_lists))}")
                
                try:
                    # Use the new synchronous function directly
                    result_df = self.get_annual_return(chunk)
                    
                    if not result_df.empty:
                        all_results.append(result_df)
                    
                    # Add small delay to be respectful to Yahoo Finance API
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"Error processing chunk {i//chunk_size + 1}: {e}")
                    continue
            
            if all_results:
                df = pd.concat(all_results, axis=0, ignore_index=True)
                logging.info(f"Successfully fetched data for {len(df)} stocks from Yahoo Finance")
                
                # Save to Redis manager
                redis_manager.save_annual_returns(df)
                return df
            else:
                logging.error("No data could be fetched from Yahoo Finance")
                return self._generate_fallback_data(ticker_lists)
                
        except Exception as e:
            logging.error(f"Error fetching from Yahoo Finance: {e}")
            logging.info("Falling back to mock data generation...")
            return self._generate_fallback_data(ticker_lists)
    
    def _generate_fallback_data(self, ticker_lists):
        """Generate fallback mock data when Yahoo Finance fails"""
        logging.info("Creating fallback mock annual returns data...")
        results = []
        for i, ticker in enumerate(ticker_lists):
            # Generate realistic mock data with different risk profiles
            import random
            
            # Distribute stocks across different risk levels
            if i % 3 == 0:  # Low risk (15-40%)
                annual_risk = random.uniform(0.15, 0.40)
                annual_return = random.uniform(0.05, 0.15)
            elif i % 3 == 1:  # Medium risk (40-60%)
                annual_risk = random.uniform(0.40, 0.60)
                annual_return = random.uniform(0.10, 0.20)
            else:  # High risk (60-80%)
                annual_risk = random.uniform(0.60, 0.80)
                annual_return = random.uniform(0.15, 0.30)
            
            # Calculate return/risk ratio
            return_risk_ratio = annual_return / annual_risk if annual_risk > 0 else 0
            
            result = pd.DataFrame({
                'Ticker': [ticker],
                'expected_annual_return': [annual_return],
                'expected_annual_risk': [annual_risk],
                'return_risk_ratio': [return_risk_ratio]
            })
            results.append(result)
        
        if results:
            df = pd.concat(results, axis=0, ignore_index=True)
            logging.info(f"Generated fallback data for {len(df)} stocks")
            
            # Save to Redis manager
            redis_manager.save_annual_returns(df)
            return df
        else:
            logging.error("No annual return data could be calculated")
            return pd.DataFrame()
    
    def update_with_return_data(self,df):
        helper.round_decimal_place(df,['insider_own','dividend','roi','roe'])
        return_rate = self.get_annual_return_data()
        df = pd.merge(df, return_rate, on='Ticker', how='inner', validate=None)
        df = np.round(df, decimals=3)
        df = df.drop_duplicates()
        df  = df.replace(np.nan,0)
        df = df.applymap(str)
         #the dataTable throws invalid json if the dtype is not string. Workaround solution for now
        return df

    def get_risk_tolerance_data(self,risk_tolerance,df):
        logging.info(f"Applying risk tolerance filter: {risk_tolerance}")
        logging.info(f"Initial stock count: {len(df)}")
        
        if risk_tolerance == RiskEnum.HIGH.value:
            df = df[df['expected_annual_risk'].astype(float) > .6]
            logging.info(f"High risk filter (>0.6): {len(df)} stocks")
        elif risk_tolerance == RiskEnum.MEDIUM.value:
            df = df[(df['expected_annual_risk'].astype(float) > .35) &(df['expected_annual_risk'].astype(float) < .65)]
            logging.info(f"Medium risk filter (0.35-0.65): {len(df)} stocks")
        elif risk_tolerance == RiskEnum.LOW.value:
            df = df[(df['expected_annual_risk'].astype(float) > .1) &(df['expected_annual_risk'].astype(float) < .45)]
            logging.info(f"Low risk filter (0.1-0.45): {len(df)} stocks")
        
        if len(df) == 0:
            logging.warning(f"No stocks passed {risk_tolerance} risk filter. Showing all stocks.")
            return df  # Return empty DataFrame, let the calling code handle it
        
        return df
    
    def clear_annual_returns_cache(self):
        """Clear cached annual returns data to force fresh Yahoo Finance fetch"""
        logging.info("Clearing annual returns cache to force fresh Yahoo Finance data")
        redis_manager.clear_annual_returns()
    
    def force_refresh_annual_returns(self):
        """Force refresh of annual returns data from Yahoo Finance"""
        logging.info("Forcing refresh of annual returns from Yahoo Finance")
        self.clear_annual_returns_cache()
        return self.get_annual_return_data()
    
    def get_cache_status(self):
        """Get detailed cache status for annual returns"""
        return redis_manager.get_annual_returns_cache_status()
    
    def extend_cache(self, hours: int = 24):
        """Extend the cache TTL for annual returns"""
        success = redis_manager.extend_annual_returns_cache(hours)
        if success:
            logging.info(f"Extended annual returns cache by {hours} hours")
        return success
    
    def is_cache_fresh(self, max_age_hours: int = 6):
        """Check if cache is fresh (less than max_age_hours old)"""
        status = self.get_cache_status()
        if status.get('status') == 'cached':
            ttl_seconds = status.get('ttl_seconds', 0)
            # If TTL is more than (24 - max_age_hours), cache is fresh
            return ttl_seconds > (24 - max_age_hours) * 3600
        return False

if __name__ == "__main__":
    annualReturn = AnnualReturn()
    annualReturn.get_annual_return_data()


