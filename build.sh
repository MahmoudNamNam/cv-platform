#!/bin/bash
# Build script for deployment platforms
echo "Building CV Platform..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
cd cv_platform
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

echo "Build complete!"

