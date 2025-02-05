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

# Create required directories
echo "Creating required directories..."
mkdir -p /home/flask/Hawaii_Cats/logs
mkdir -p /tmp/hawaiicats_logs
mkdir -p /home/flask/Hawaii_Cats/run

# Set correct permissions
echo "Setting correct permissions..."
sudo chown -R www-data:www-data /home/flask/Hawaii_Cats
sudo chmod -R 755 /home/flask/Hawaii_Cats
sudo chown www-data:www-data /tmp/hawaiicats_logs
sudo chmod 755 /tmp/hawaiicats_logs

# Clean up any existing socket file
echo "Cleaning up socket..."
sudo rm -f /home/flask/Hawaii_Cats/run/gunicorn.socket

# Install/update Python packages in virtual environment
echo "Updating Python packages..."
/home/flask/Hawaii_Cats/venv/bin/pip install -r requirements.txt

# Copy and reload service files
echo "Updating service files..."
sudo cp deployment/gunicorn.service /etc/systemd/system/hawaii-cats.service
sudo cp deployment/nginx.conf /etc/nginx/sites-available/hawaii-cats.conf

# Update nginx configuration
echo "Configuring nginx..."
sudo ln -sf /etc/nginx/sites-available/hawaii-cats.conf /etc/nginx/sites-enabled/hawaii-cats.conf
sudo rm -f /etc/nginx/sites-enabled/default

# Reload systemd and restart services
echo "Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl stop hawaii-cats nginx
sudo pkill gunicorn || true  # Kill any stray gunicorn processes
sleep 2  # Wait for processes to stop
sudo systemctl start hawaii-cats
sleep 2  # Wait for gunicorn to fully start
sudo systemctl start nginx

# Health check
echo "Performing health check..."
MAX_RETRIES=10
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost > /dev/null; then
        echo "Deployment successful! Application is responding."
        exit 0
    fi
    echo "Waiting for application to respond... (Attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 3
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

echo "Warning: Application health check failed after $MAX_RETRIES attempts."
echo "Checking service status..."
sudo systemctl status hawaii-cats
sudo systemctl status nginx
echo "Checking logs..."
sudo tail -n 50 /var/log/nginx/error.log
echo "You may need to check the logs or restore from backup at $BACKUP_DIR"
exit 1
