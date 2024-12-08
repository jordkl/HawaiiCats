# Deployment Configuration

This directory contains reference configuration files for deploying the Hawaii Cats application.

## Files

- `gunicorn.service`: Systemd service configuration for Gunicorn
  - Location: `/etc/systemd/system/gunicorn.service`
  - Uses Unix socket at `/run/gunicorn/gunicorn.socket`
  
- `nginx.conf`: NGINX configuration
  - Location: `/etc/nginx/sites-enabled/default`
  - Proxies requests to Gunicorn socket
  - Handles SSL/TLS termination

## Setup

1. Create socket directory:
```bash
sudo mkdir -p /run/gunicorn
sudo chown www-data:www-data /run/gunicorn
```

2. Copy configuration files:
```bash
sudo cp gunicorn.service /etc/systemd/system/
sudo cp nginx.conf /etc/nginx/sites-enabled/default
```

3. Reload and restart services:
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn nginx
```
