#!/usr/bin/env python3
"""
Test script for the new async data fetching system
"""

import asyncio
import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_fetcher import fetch_stock_data_sync, fetch_stock_data_async
from services.message_queue import enqueue_stock_data_fetch, TaskPriority, message_queue
from services.async_scheduler import get_scheduler_status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sync_data_fetching():
    """Test synchronous data fetching"""
    logger.info("Testing synchronous data fetching...")
    
    try:
        # Test fetching S&P 500 Technology sector data
        result = fetch_stock_data_sync('S&P 500', 'Technology')
        
        if result.success:
            logger.info(f"✅ Sync fetch successful!")
            logger.info(f"   Source: {result.source.value}")
            logger.info(f"   Data records: {len(result.data)}")
            logger.info(f"   Columns: {list(result.data.columns)}")
            
            if not result.data.empty:
                logger.info(f"   Sample data:")
                logger.info(f"   {result.data.head(3)}")
            
            return True
        else:
            logger.error(f"❌ Sync fetch failed: {result.error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Sync fetch exception: {e}")
        return False

async def test_async_data_fetching():
    """Test asynchronous data fetching"""
    logger.info("Testing asynchronous data fetching...")
    
    try:
        # Test fetching S&P 500 data
        result = await fetch_stock_data_async('S&P 500', 'Any')
        
        if result.success:
            logger.info(f"✅ Async fetch successful!")
            logger.info(f"   Source: {result.source.value}")
            logger.info(f"   Data records: {len(result.data)}")
            return True
        else:
            logger.error(f"❌ Async fetch failed: {result.error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Async fetch exception: {e}")
        return False

def test_message_queue():
    """Test message queue functionality"""
    logger.info("Testing message queue...")
    
    try:
        # Enqueue a test task
        task_id = enqueue_stock_data_fetch(
            index='S&P 500',
            sector='Technology',
            priority=TaskPriority.HIGH
        )
        
        logger.info(f"✅ Task queued successfully!")
        logger.info(f"   Task ID: {task_id}")
        
        # Get queue stats
        stats = message_queue.get_queue_stats()
        logger.info(f"   Queue stats: {stats}")
        
        # Get task status
        task = message_queue.get_task_status(task_id)
        if task:
            logger.info(f"   Task status: {task.status.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Message queue test failed: {e}")
        return False

def test_scheduler_status():
    """Test scheduler status"""
    logger.info("Testing scheduler status...")
    
    try:
        status = get_scheduler_status()
        logger.info(f"✅ Scheduler status retrieved!")
        logger.info(f"   Running: {status.get('running', False)}")
        logger.info(f"   Queue stats: {status.get('queue_stats', {})}")
        logger.info(f"   Schedule config: {status.get('schedule_config', {})}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Scheduler status test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting async system tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Sync Data Fetching", test_sync_data_fetching),
        ("Message Queue", test_message_queue),
        ("Scheduler Status", test_scheduler_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Results Summary:")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The async system is working correctly.")
        return True
    else:
        logger.error("⚠️  Some tests failed. Please check the logs above.")
        return False

def run_async_test():
    """Run async test separately"""
    logger.info("Testing async data fetching...")
    try:
        result = asyncio.run(test_async_data_fetching())
        return result
    except Exception as e:
        logger.error(f"❌ Async test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        
        # Run async test separately
        logger.info("\n" + "=" * 50)
        logger.info("📋 Running Async Test Separately")
        logger.info("-" * 30)
        async_success = run_async_test()
        
        if success and async_success:
            logger.info("🎉 All tests passed! The async system is working correctly.")
            sys.exit(0)
        else:
            logger.error("⚠️  Some tests failed. Please check the logs above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
