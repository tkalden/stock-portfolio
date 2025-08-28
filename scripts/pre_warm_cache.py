#!/usr/bin/env python3
"""
Pre-warm cache script for Stocknity
This script pre-warms the annual returns cache to avoid cold starts
"""

import sys
import os
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from services.annualReturn import AnnualReturn

def main():
    """Pre-warm the annual returns cache"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting cache pre-warm process...")
    
    try:
        annual_return = AnnualReturn()
        
        # Check if cache is already fresh
        if annual_return.is_cache_fresh():
            logger.info("Cache is already fresh, no need to pre-warm")
            return True
        
        # Pre-warm the cache
        success = annual_return.pre_warm_cache()
        
        if success:
            logger.info("Cache pre-warmed successfully")
            return True
        else:
            logger.error("Failed to pre-warm cache")
            return False
            
    except Exception as e:
        logger.error(f"Error during cache pre-warm: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
