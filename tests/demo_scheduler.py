#!/usr/bin/env python3
"""
Demo script to show scheduler starting with different configurations
"""

import os
import sys
import time
import asyncio

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from services.async_scheduler import AsyncScheduler

def demo_scheduler_config():
    """Demo the scheduler with current configuration"""
    print("🚀 Scheduler Configuration Demo")
    print("=" * 50)
    
    # Show current configuration
    config = {
        'start_delay': os.getenv('SCHEDULER_START_DELAY_MINUTES', '5'),
        'data_interval': os.getenv('SCHEDULER_DATA_FETCH_INTERVAL_MINUTES', '1440'),
        'health_interval': os.getenv('SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES', '60'),
        'cleanup_interval': os.getenv('SCHEDULER_CLEANUP_INTERVAL_DAYS', '7')
    }
    
    print(f"📋 Current Configuration:")
    print(f"  Start Delay: {config['start_delay']} minutes")
    print(f"  Data Fetch Interval: {config['data_interval']} minutes")
    print(f"  Health Check Interval: {config['health_interval']} minutes")
    print(f"  Cleanup Interval: {config['cleanup_interval']} days")
    
    # Create scheduler instance
    scheduler = AsyncScheduler()
    
    print(f"\n🔧 Scheduler Configuration:")
    print(f"  Schedule Config: {scheduler.schedule_config}")
    
    print(f"\n✅ Demo complete!")
    print(f"\n💡 To start the scheduler with this configuration:")
    print(f"   1. Run: python main.py")
    print(f"   2. Start scheduler: curl -X POST http://localhost:5001/api/scheduler/start")
    print(f"   3. Check status: curl http://localhost:5001/api/scheduler/status")

def demo_quick_start():
    """Demo with quick start configuration"""
    print("\n⚡ Quick Start Demo (1 minute intervals)")
    print("=" * 50)
    
    # Set quick start environment variables
    os.environ['SCHEDULER_START_DELAY_MINUTES'] = '1'
    os.environ['SCHEDULER_DATA_FETCH_INTERVAL_MINUTES'] = '1'
    os.environ['SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES'] = '1'
    
    # Create scheduler instance
    scheduler = AsyncScheduler()
    
    print(f"📋 Quick Start Configuration:")
    print(f"  Start Delay: {scheduler.schedule_config['start_delay_minutes']} minutes")
    print(f"  Data Fetch Interval: {scheduler.schedule_config['data_fetch_interval']} minutes")
    print(f"  Health Check Interval: {scheduler.schedule_config['health_check_interval']} minutes")
    
    print(f"\n✅ Quick start demo complete!")
    print(f"\n💡 This configuration will:")
    print(f"   - Start data fetching in 1 minute")
    print(f"   - Fetch data every 1 minute")
    print(f"   - Run health checks every 1 minute")

if __name__ == "__main__":
    demo_scheduler_config()
    demo_quick_start()
