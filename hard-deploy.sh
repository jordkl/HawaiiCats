#!/bin/bash

# Exit on any error
set -e

echo "Starting force pull deployment..."

# Force pull latest changes
echo "Force pulling latest changes from GitHub..."
./git-force-sync.sh pull main

# Create logs directory if it doesn't exist
echo "Creating logs directory..."
mkdir -p /home/flask/Hawaii_Cats/logs

# Set correct permissions
echo "Setting correct permissions..."
sudo chown -R www-data:www-data /home/flask/Hawaii_Cats
sudo chmod -R 755 /home/flask/Hawaii_Cats

# Copy service files
echo "Updating service files..."
sudo cp deployment/gunicorn.service /etc/systemd/system/hawaii-cats.service
sudo systemctl daemon-reload

# Restart services
echo "Restarting services..."
sudo systemctl restart hawaii-cats
sudo systemctl restart nginx

echo "Force pull deployment completed successfully!"
