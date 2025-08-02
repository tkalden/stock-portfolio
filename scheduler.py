import logging
import threading
import time
from datetime import datetime

import schedule

from services.annualReturn import AnnualReturn
from services.sourceDataMapper import SourceDataMapperService
from services.strengthCalculator import StrengthCalculator
from utilities.redis_data import redis_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataScheduler:
    def __init__(self):
        self.source_mapper = SourceDataMapperService()
        self.annual_return = AnnualReturn()
        self.strength_calculator = StrengthCalculator()
        self.running = False

    def fetch_and_cache_stock_data(self):
        """Fetch and cache stock data for all sectors"""
        logger.info("Starting scheduled stock data fetch and cache")
        
        try:
            # Clear existing stock data cache
            redis_manager.clear_expired_data()
            
            # Define indices to cache
            indices = ['S&P 500', 'DJIA']
            
            for index in indices:
                # Fetch and cache general data first
                logger.info(f"Fetching and caching general {index} data")
                general_df = self.source_mapper.get_data_by_index_sector(index, 'Any')
                if not general_df.empty:
                    redis_manager.save_stock_data(general_df, index, 'Any')
                    logger.info(f"Cached general {index} data with {len(general_df)} records")
                
                # Fetch and cache data for each sector
                from utilities.constant import SECTORS
                for sector in SECTORS:
                    logger.info(f"Fetching and caching data for {index}:{sector}")
                    df = self.source_mapper.get_data_by_index_sector(index, sector)
                    if not df.empty:
                        redis_manager.save_stock_data(df, index, sector)
                        logger.info(f"Cached {index}:{sector} data with {len(df)} records")
                    else:
                        logger.warning(f"No data found for {index}:{sector}")
            
            logger.info("Completed scheduled stock data fetch and cache")
            
        except Exception as e:
            logger.error(f"Error in scheduled stock data fetch: {e}")

    def fetch_and_cache_annual_returns(self):
        """Fetch and cache annual returns data"""
        logger.info("Starting scheduled annual returns fetch and cache")
        
        try:
            # Clear existing annual returns cache
            redis_manager.clear_expired_data()
            
            # Fetch and cache annual returns
            annual_returns_df = self.annual_return.get_annual_return_data()
            if not annual_returns_df.empty:
                redis_manager.save_annual_returns(annual_returns_df)
                logger.info(f"Cached annual returns data with {len(annual_returns_df)} records")
            else:
                logger.warning("No annual returns data to cache")
            
            logger.info("Completed scheduled annual returns fetch and cache")
            
        except Exception as e:
            logger.error(f"Error in scheduled annual returns fetch: {e}")

    def precalculate_and_cache_strength_data(self):
        """Precalculate and cache all strength data"""
        logger.info("Starting scheduled strength data precalculation")
        
        try:
            # Clear existing strength data cache
            self.strength_calculator.clear_strength_cache()
            
            # Precalculate all strength data combinations
            self.strength_calculator.precalculate_all_strength_data()
            
            logger.info("Completed scheduled strength data precalculation")
            
        except Exception as e:
            logger.error(f"Error in scheduled strength data precalculation: {e}")

    def daily_data_refresh(self):
        """Complete daily data refresh at 8 AM"""
        logger.info("Starting daily data refresh at 8 AM")
        
        try:
            # Step 1: Fetch and cache stock data
            self.fetch_and_cache_stock_data()
            
            # Step 2: Fetch and cache annual returns
            self.fetch_and_cache_annual_returns()
            
            # Step 3: Precalculate and cache strength data
            self.precalculate_and_cache_strength_data()
            
            logger.info("Completed daily data refresh")
            
        except Exception as e:
            logger.error(f"Error in daily data refresh: {e}")

    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        # Schedule daily data refresh at 8 AM
        schedule.every().day.at("08:00").do(self.daily_data_refresh)
        
        # Schedule individual tasks for flexibility
        schedule.every().day.at("08:05").do(self.fetch_and_cache_stock_data)
        schedule.every().day.at("08:10").do(self.fetch_and_cache_annual_returns)
        schedule.every().day.at("08:15").do(self.precalculate_and_cache_strength_data)
        
        logger.info("Scheduler started with daily refresh at 8 AM")
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Scheduler thread started")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("Scheduler stopped")

    def check_cache_status(self):
        """Check the status of all cached data"""
        logger.info("Checking cache status...")
        
        try:
            # Check stock data cache
            stock_keys = redis_manager.r.keys("stock_data:*")
            logger.info(f"Stock data cache entries: {len(stock_keys)}")
            
            # Check annual returns cache
            annual_keys = redis_manager.r.keys("annual_returns")
            logger.info(f"Annual returns cache entries: {len(annual_keys)}")
            
            # Check strength data cache
            strength_cache = redis_manager.get_strength_cache_status()
            logger.info(f"Strength data cache entries: {len(strength_cache)}")
            
            # Log cache details
            for key, info in strength_cache.items():
                logger.info(f"  {key}: {info['expires_in']}")
            
            return {
                'stock_data': len(stock_keys),
                'annual_returns': len(annual_keys),
                'strength_data': len(strength_cache),
                'strength_details': strength_cache
            }
            
        except Exception as e:
            logger.error(f"Error checking cache status: {e}")
            return {}

    def clear_all_cache(self):
        """Clear all cached data"""
        logger.info("Clearing all cached data...")
        
        try:
            # Clear stock data
            stock_keys = redis_manager.r.keys("stock_data:*")
            if stock_keys:
                redis_manager.r.delete(*stock_keys)
                logger.info(f"Cleared {len(stock_keys)} stock data entries")
            
            # Clear annual returns
            annual_keys = redis_manager.r.keys("annual_returns")
            if annual_keys:
                redis_manager.r.delete(*annual_keys)
                logger.info(f"Cleared {len(annual_keys)} annual returns entries")
            
            # Clear strength data
            self.strength_calculator.clear_strength_cache()
            
            logger.info("All cached data cleared")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

# Global scheduler instance
data_scheduler = DataScheduler() 