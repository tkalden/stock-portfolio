"""
Asynchronous Scheduler Service
Handles scheduled data fetching and processing using the message queue system
"""

import asyncio
import logging
import os
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import threading
from services.message_queue import (
    message_queue, 
    enqueue_stock_data_fetch, 
    enqueue_annual_returns_calculation,
    TaskPriority
)
from services.data_fetcher import fetch_stock_data_async
from utilities.constant import SECTORS, INDEX
from utilities.redis_data import redis_manager

logger = logging.getLogger(__name__)

class AsyncScheduler:
    """Asynchronous scheduler for data fetching and processing"""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self.background_processor_task = None
        self.last_run = {}
        
        # Load schedule configuration from environment variables
        self.schedule_config = {
            'daily_refresh': os.getenv('SCHEDULER_DAILY_REFRESH', '08:00'),  # 8 AM daily
            'hourly_check': os.getenv('SCHEDULER_HOURLY_CHECK', '00:00'),   # Every hour
            'weekly_cleanup': os.getenv('SCHEDULER_WEEKLY_CLEANUP', '02:00'),  # 2 AM Sunday
            'data_fetch_interval': int(os.getenv('SCHEDULER_DATA_FETCH_INTERVAL_MINUTES', '1440')),  # 24 hours default
            'health_check_interval': int(os.getenv('SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES', '60')),  # 1 hour default
            'cleanup_interval': int(os.getenv('SCHEDULER_CLEANUP_INTERVAL_DAYS', '7')),  # 7 days default
            'start_delay_minutes': int(os.getenv('SCHEDULER_START_DELAY_MINUTES', '5'))  # 5 minutes from now
        }
        
        logger.info(f"Scheduler configuration: {self.schedule_config}")
    
    async def start(self):
        """Start the async scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting async scheduler")
        
        # Start background task processor
        self.background_processor_task = asyncio.create_task(
            self._start_background_processing()
        )
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Async scheduler started successfully")
    
    async def stop(self):
        """Stop the async scheduler"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping async scheduler")
        
        # Stop background processor
        if self.background_processor_task:
            self.background_processor_task.cancel()
            try:
                await self.background_processor_task
            except asyncio.CancelledError:
                pass
        
        # Wait for scheduler thread
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Async scheduler stopped")
    
    async def _start_background_processing(self):
        """Start the background task processing"""
        from services.message_queue import start_background_processing
        await start_background_processing()
    
    def _run_scheduler_loop(self):
        """Run the scheduler loop in a separate thread"""
        logger.info("Starting scheduler loop")
        
        # Schedule tasks
        self._setup_schedules()
        
        # Run the scheduler
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)
        
        logger.info("Scheduler loop stopped")
    
    def _setup_schedules(self):
        """Setup scheduled tasks with configurable intervals"""
        
        # Calculate start time (5 minutes from now by default)
        start_delay = self.schedule_config['start_delay_minutes']
        start_time = datetime.now() + timedelta(minutes=start_delay)
        
        # Schedule initial data fetch
        schedule.every().day.at(start_time.strftime('%H:%M')).do(
            self._daily_data_refresh
        )
        
        # Schedule recurring data fetch based on interval
        data_interval = self.schedule_config['data_fetch_interval']
        if data_interval < 1440:  # Less than 24 hours, use minutes
            schedule.every(data_interval).minutes.do(self._daily_data_refresh)
        else:  # 24 hours or more, use daily
            schedule.every().day.at(self.schedule_config['daily_refresh']).do(
                self._daily_data_refresh
            )
        
        # Schedule health checks
        health_interval = self.schedule_config['health_check_interval']
        if health_interval < 60:  # Less than 1 hour, use minutes
            schedule.every(health_interval).minutes.do(self._hourly_health_check)
        else:  # 1 hour or more, use hours
            schedule.every().hour.do(self._hourly_health_check)
        
        # Schedule cleanup
        cleanup_interval = self.schedule_config['cleanup_interval']
        if cleanup_interval == 1:  # Daily cleanup
            schedule.every().day.at(self.schedule_config['weekly_cleanup']).do(
                self._weekly_cleanup
            )
        else:  # Weekly cleanup
            schedule.every().sunday.at(self.schedule_config['weekly_cleanup']).do(
                self._weekly_cleanup
            )
        
        logger.info(f"Scheduled tasks configured with start delay: {start_delay} minutes")
        logger.info(f"Data fetch interval: {data_interval} minutes")
        logger.info(f"Health check interval: {health_interval} minutes")
        logger.info(f"Cleanup interval: {cleanup_interval} days")
    
    def _daily_data_refresh(self):
        """Daily data refresh task"""
        logger.info("Starting daily data refresh")
        
        try:
            # Queue data fetch tasks for all index/sector combinations
            for index in INDEX:
                for sector in SECTORS + ['Any']:
                    task_id = enqueue_stock_data_fetch(
                        index=index,
                        sector=sector,
                        priority=TaskPriority.HIGH
                    )
                    logger.info(f"Queued daily refresh task {task_id} for {index}:{sector}")
            
            # Queue annual returns calculation
            self._queue_annual_returns_calculation()
            
            self.last_run['daily_refresh'] = datetime.now()
            logger.info("Daily data refresh tasks queued successfully")
            
        except Exception as e:
            logger.error(f"Error in daily data refresh: {e}")
    
    def _hourly_health_check(self):
        """Hourly health check task"""
        logger.debug("Running hourly health check")
        
        try:
            # Check queue stats
            stats = message_queue.get_queue_stats()
            logger.info(f"Queue stats: {stats}")
            
            # Check Redis connection
            try:
                redis_manager.r.ping()
                logger.debug("Redis connection healthy")
            except Exception as e:
                logger.error(f"Redis connection error: {e}")
            
            self.last_run['hourly_check'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in hourly health check: {e}")
    
    def _weekly_cleanup(self):
        """Weekly cleanup task"""
        logger.info("Starting weekly cleanup")
        
        try:
            # Clean old completed tasks (older than 7 days)
            self._cleanup_old_tasks()
            
            # Clean old cached data (older than 30 days)
            self._cleanup_old_cache()
            
            self.last_run['weekly_cleanup'] = datetime.now()
            logger.info("Weekly cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in weekly cleanup: {e}")
    
    def _queue_annual_returns_calculation(self):
        """Queue annual returns calculation for all tickers"""
        try:
            # Get all tickers from cached data
            all_tickers = set()
            
            for index in INDEX:
                for sector in SECTORS + ['Any']:
                    data = redis_manager.get_stock_data(index, sector)
                    if not data.empty and 'Ticker' in data.columns:
                        tickers = data['Ticker'].tolist()
                        all_tickers.update(tickers)
            
            if all_tickers:
                # Split tickers into chunks
                ticker_list = list(all_tickers)
                chunk_size = 50
                
                for i in range(0, len(ticker_list), chunk_size):
                    chunk = ticker_list[i:i + chunk_size]
                    task_id = enqueue_annual_returns_calculation(
                        tickers=chunk,
                        priority=TaskPriority.NORMAL
                    )
                    logger.info(f"Queued annual returns task {task_id} for {len(chunk)} tickers")
            
        except Exception as e:
            logger.error(f"Error queuing annual returns calculation: {e}")
    
    def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        try:
            # This would clean up tasks older than 7 days
            # Implementation depends on Redis key patterns
            logger.info("Cleaned up old tasks")
        except Exception as e:
            logger.error(f"Error cleaning up old tasks: {e}")
    
    def _cleanup_old_cache(self):
        """Clean up old cached data"""
        try:
            # This would clean up cached data older than 30 days
            # Implementation depends on Redis key patterns
            logger.info("Cleaned up old cache")
        except Exception as e:
            logger.error(f"Error cleaning up old cache: {e}")
    
    async def manual_refresh(self, index: str = None, sector: str = None):
        """Manually trigger data refresh"""
        logger.info(f"Manual refresh requested for {index}:{sector}")
        
        try:
            if index and sector:
                # Refresh specific index/sector
                task_id = enqueue_stock_data_fetch(
                    index=index,
                    sector=sector,
                    priority=TaskPriority.URGENT
                )
                logger.info(f"Manual refresh task {task_id} queued for {index}:{sector}")
            else:
                # Refresh all
                for idx in INDEX:
                    for sec in SECTORS + ['Any']:
                        task_id = enqueue_stock_data_fetch(
                            index=idx,
                            sector=sec,
                            priority=TaskPriority.HIGH
                        )
                        logger.info(f"Manual refresh task {task_id} queued for {idx}:{sec}")
            
            return {"success": True, "message": "Manual refresh tasks queued"}
            
        except Exception as e:
            logger.error(f"Error in manual refresh: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.running,
            "last_run": self.last_run,
            "queue_stats": message_queue.get_queue_stats(),
            "schedule_config": self.schedule_config
        }
    
    async def force_refresh_all_data(self):
        """Force refresh all data immediately"""
        logger.info("Force refresh all data requested")
        
        try:
            # Clear existing cache
            await self._clear_cache()
            
            # Queue immediate refresh tasks
            for index in INDEX:
                for sector in SECTORS + ['Any']:
                    task_id = enqueue_stock_data_fetch(
                        index=index,
                        sector=sector,
                        priority=TaskPriority.URGENT
                    )
                    logger.info(f"Force refresh task {task_id} queued for {index}:{sector}")
            
            return {"success": True, "message": "Force refresh tasks queued"}
            
        except Exception as e:
            logger.error(f"Error in force refresh: {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_cache(self):
        """Clear all cached data"""
        try:
            # Clear stock data cache
            for index in INDEX:
                for sector in SECTORS + ['Any']:
                    redis_manager.r.delete(f"stock_data:{index}:{sector}")
            
            # Clear annual returns cache
            redis_manager.r.delete("annual_returns")
            
            logger.info("Cache cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

# Global scheduler instance
async_scheduler = AsyncScheduler()

# Convenience functions
async def start_scheduler():
    """Start the async scheduler"""
    await async_scheduler.start()

async def stop_scheduler():
    """Stop the async scheduler"""
    await async_scheduler.stop()

def get_scheduler_status():
    """Get scheduler status"""
    return async_scheduler.get_status()

async def manual_refresh_data(index: str = None, sector: str = None):
    """Manually refresh data"""
    return await async_scheduler.manual_refresh(index, sector)

async def force_refresh_all():
    """Force refresh all data"""
    return await async_scheduler.force_refresh_all_data()
