#!/usr/bin/env python3
"""
Main entry point for the Flask application
"""
from __init__ import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 