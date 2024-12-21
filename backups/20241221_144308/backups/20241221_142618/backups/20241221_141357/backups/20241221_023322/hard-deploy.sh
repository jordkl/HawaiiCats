#!/bin/bash

# Exit on any error
set -e

echo "Starting force pull deployment..."

# Create backup of current state
echo "Creating backup..."
BACKUP_DIR="/home/flask/Hawaii_Cats/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /home/flask/Hawaii_Cats/* "$BACKUP_DIR/" 2>/dev/null || true

# Force pull latest changes
echo "Force pulling latest changes from GitHub..."
./git-force-sync.sh pull main

# Create logs directory if it doesn't exist
echo "Creating logs directory..."
mkdir -p /home/flask/Hawaii_Cats/logs

# Install/update Python packages
echo "Updating Python packages..."
python3 -m pip install -r requirements.txt

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

# Health check
echo "Performing health check..."
MAX_RETRIES=5
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:80 > /dev/null; then
        echo "Deployment successful! Application is responding."
        exit 0
    fi
    echo "Waiting for application to respond..."
    sleep 5
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

echo "Warning: Application health check failed. You may need to check the logs or restore from backup at $BACKUP_DIR"
