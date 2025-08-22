#!/usr/bin/env python3
"""
Test script to demonstrate scheduler configuration with environment variables
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_scheduler_config():
    """Test the scheduler configuration"""
    print("🔧 Testing Scheduler Configuration")
    print("=" * 50)
    
    # Test environment variables
    config_vars = {
        'SCHEDULER_START_DELAY_MINUTES': '5',
        'SCHEDULER_DATA_FETCH_INTERVAL_MINUTES': '1440',
        'SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES': '60',
        'SCHEDULER_CLEANUP_INTERVAL_DAYS': '7',
        'SCHEDULER_DAILY_REFRESH': '08:00',
        'SCHEDULER_HOURLY_CHECK': '00:00',
        'SCHEDULER_WEEKLY_CLEANUP': '02:00'
    }
    
    print("📋 Current Environment Variables:")
    for var, default in config_vars.items():
        value = os.getenv(var, default)
        print(f"  {var}: {value}")
    
    print("\n🚀 Example Configurations:")
    
    # Development configuration
    print("\n1. Development (frequent updates):")
    print("   export SCHEDULER_START_DELAY_MINUTES=1")
    print("   export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=30")
    print("   export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=15")
    
    # High-frequency configuration
    print("\n2. High-frequency (every 5 minutes):")
    print("   export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=5")
    print("   export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=5")
    
    # Production configuration
    print("\n3. Production (daily updates):")
    print("   export SCHEDULER_START_DELAY_MINUTES=5")
    print("   export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=1440")
    print("   export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=60")
    
    print("\n✅ Configuration test complete!")
    print("\n💡 To test with different settings:")
    print("   1. Set environment variables")
    print("   2. Run: python main.py")
    print("   3. Start scheduler: curl -X POST http://localhost:5001/api/scheduler/start")

if __name__ == "__main__":
    test_scheduler_config()
