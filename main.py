#!/usr/bin/env python3
"""
Stocknity - Advanced Stock Portfolio Management System
Main entry point for the Flask application
Updated: 2025-08-25 - Fixed bs4 import issues
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

from core.app import app

if __name__ == '__main__':
    # Use environment variable for port, default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
