import logging

import numpy as np
import pandas as pd

from enums.enum import StockType
from services.annualReturn import AnnualReturn
from services.sourceDataMapper import SourceDataMapperService
from utilities.redis_data import redis_manager

SourceDataMapperService = SourceDataMapperService()
AnnualReturn = AnnualReturn()

class StrengthCalculator:

    def __init__(self):
        self.cache_key_prefix = "strength_data"
    
    def _get_cache_key(self, stock_type, sector, index):
        """Generate cache key for strength data"""
        return f"{self.cache_key_prefix}:{stock_type}:{sector}:{index}"
    
    def _get_strength_from_cache(self, stock_type, sector, index):
        """Get strength data from Redis cache"""
        cache_key = self._get_cache_key(stock_type, sector, index)
        df = redis_manager.get_strength_data(cache_key)
        if not df.empty:
            logging.debug(f"Retrieved strength data from cache for {stock_type}:{sector}:{index}")
            return df
        return pd.DataFrame()
    
    def _save_strength_to_cache(self, df, stock_type, sector, index):
        """Save strength data to Redis cache"""
        cache_key = self._get_cache_key(stock_type, sector, index)
        redis_manager.save_strength_data(df, cache_key)
        logging.debug(f"Saved strength data to cache for {stock_type}:{sector}:{index}")

    def calculate_strength_value(self, stock_type, sector, index):
        """Calculate strength value with caching"""
        logging.debug(f"Calculating strength value for {stock_type} Stock")
        
        # Try to get from cache first
        cached_df = self._get_strength_from_cache(stock_type, sector, index)
        if not cached_df.empty:
            return cached_df
        
        # Calculate if not in cache
        logging.info(f"Strength data not found in cache for {stock_type}:{sector}:{index}, calculating...")
        df = SourceDataMapperService.get_data_by_index_sector(index, sector)
        df = AnnualReturn.update_with_return_data(df)
        avg_metric_df = SourceDataMapperService.get_avg_metric_per_sector(sector)
        
        # Calculate strength
        df = self._calculate_strength(df, avg_metric_df, stock_type)
        
        # Save to cache
        self._save_strength_to_cache(df, stock_type, sector, index)
        
        return df
    
    def _calculate_strength(self, df, avg_metric_df, stock_type):
        """Calculate strength values for the dataframe"""
        attributes = ["dividend", "pe", "fpe", "pb", "beta", "return_risk_ratio"]
        df["strength"] = 0
        
        for col in attributes:
            df[col].replace('nan', np.nan, inplace=True)
            df[col].replace('None', np.nan, inplace=True)
            
            if col == 'beta':
                df["strength"] = df["strength"] - np.where(df[col].isnull(), 0, df[col].astype(float))
            elif col == 'return_risk_ratio':
                df["strength"] = df["strength"] + np.where(df[col].isnull(), 0, df[col].astype(float))
            else:
                new_col = np.where(df[col].isnull(), 0, df[col].astype(float) - avg_metric_df[col])
                new_col = np.divide(1, avg_metric_df[col]) * new_col  # percentage change
                if col == 'dividend':
                    df["strength"] = df["strength"] + new_col
                else:
                    df["strength"] = df["strength"] - new_col
        
        if stock_type == StockType.VALUE.value:
            df["strength"] = 1 * df["strength"]
        elif stock_type == StockType.GROWTH.value:
            df["strength"] = -1 * df["strength"]
        else:
            raise ValueError("Stock Type must be Value or Growth")
        
        df = df.replace(np.nan, 0)
        df = np.round(df, decimals=3)
        df = df.sort_values(by=["strength"], ascending=[False])
        
        return df
    
    def clear_strength_cache(self):
        """Clear all strength data from cache"""
        logging.info("Clearing strength data cache")
        redis_manager.clear_strength_cache(self.cache_key_prefix)
    
    def precalculate_all_strength_data(self):
        """Precalculate strength data for all combinations and cache them"""
        logging.info("Starting precalculation of all strength data")
        
        from utilities.constant import SECTORS
        stock_types = [StockType.VALUE.value, StockType.GROWTH.value]
        indices = ["S&P 500", "DJIA"]
        
        total_combinations = len(SECTORS) * len(stock_types) * len(indices)
        current = 0
        
        for index in indices:
            for sector in SECTORS:
                for stock_type in stock_types:
                    current += 1
                    logging.info(f"Precalculating strength data ({current}/{total_combinations}): {stock_type}:{sector}:{index}")
                    
                    try:
                        # Calculate and cache strength data
                        df = SourceDataMapperService.get_data_by_index_sector(index, sector)
                        df = AnnualReturn.update_with_return_data(df)
                        avg_metric_df = SourceDataMapperService.get_avg_metric_per_sector(sector)
                        df = self._calculate_strength(df, avg_metric_df, stock_type)
                        self._save_strength_to_cache(df, stock_type, sector, index)
                        
                        logging.info(f"Successfully cached strength data for {stock_type}:{sector}:{index} ({len(df)} stocks)")
                    except Exception as e:
                        logging.error(f"Error precalculating strength data for {stock_type}:{sector}:{index}: {e}")
        
        logging.info("Completed precalculation of all strength data")