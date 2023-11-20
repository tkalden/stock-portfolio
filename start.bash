#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

source ~/.bash_profile

# Start the Flask app
export FLASK_APP=main.py
flask run
