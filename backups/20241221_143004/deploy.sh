#!/bin/bash

# Exit on any error
set -e

echo "Starting deployment..."

# Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull

# Create logs directory if it doesn't exist
echo "Creating logs directory..."
mkdir -p /home/flask/Hawaii_Cats/logs

# Set correct permissions
echo "Setting correct permissions..."
sudo chown -R www-data:www-data /home/flask/Hawaii_Cats
sudo chmod -R 755 /home/flask/Hawaii_Cats

# Ensure Gunicorn config is correct
echo "Updating Gunicorn configuration..."
sudo tee /etc/gunicorn.d/gunicorn.py > /dev/null << 'EOF'
bind = 'unix:/run/gunicorn/gunicorn.socket'
workers = 5
timeout = 60
keepalive = 65
EOF

# Ensure Nginx config is correct
echo "Updating Nginx configuration..."
sudo tee /etc/nginx/sites-enabled/default > /dev/null << 'EOF'
upstream app_server {
    server unix:/run/gunicorn/gunicorn.socket fail_timeout=0;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server ipv6only=on;

    root /usr/share/nginx/html;
    index index.html index.htm;

    client_max_body_size 4G;
    server_name _;

    keepalive_timeout 65;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_redirect off;
            proxy_buffering off;

            proxy_pass http://app_server;
    }
}

server {
    root /usr/share/nginx/html;
    index index.html index.htm;

    client_max_body_size 4G;
    server_name hawaiicats.org;

    keepalive_timeout 65;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_redirect off;
            proxy_buffering off;

            proxy_pass http://app_server;
    }

    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/hawaiicats.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hawaiicats.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = hawaiicats.org) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    listen [::]:80;
    server_name hawaiicats.org;
    return 404;
}
EOF

# Restart services
echo "Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Checking service status..."
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo "Deployment complete!"
