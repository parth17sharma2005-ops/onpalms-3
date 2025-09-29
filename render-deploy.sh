#!/bin/bash
# render-deploy.sh - Script to run on Render

# Install dependencies
pip install -r requirements_simple.txt

# Start the application
gunicorn app_simple:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
