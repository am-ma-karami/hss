#!/bin/bash

# Download the model files
echo "Downloading model files"
python test.py

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Import data from config.json
echo "Import data"
python manage.py import_data

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000