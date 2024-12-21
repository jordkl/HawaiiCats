# Hawaii Cats Deployment Guide

## Project Structure
The project follows this import structure:
- All imports from the `app` package should use absolute imports starting with `app.`
- Example: `from app.tools.cat_simulation import DEFAULT_PARAMS`
- Never use relative imports like `from tools.cat_simulation`

## Environment Setup
1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Environment Variables:
- Copy `deployment/env.example` to `.env.local` for local development
- Update the values in `.env.local` with your actual configuration
- Set up Firebase credentials in `/home/flask/Hawaii_Cats/app/firebase-credentials.json`
- Set `ENABLE_FIREBASE_SYNC=false` in `.env.local` if you don't have Firebase credentials

## Deployment Steps
1. Copy service files:
```bash
sudo cp deployment/gunicorn.service /etc/systemd/system/hawaii-cats.service
sudo cp deployment/nginx.conf /etc/nginx/sites-available/hawaii-cats
sudo ln -s /etc/nginx/sites-available/hawaii-cats /etc/nginx/sites-enabled/
```

2. Create required directories:
```bash
sudo mkdir -p /run/gunicorn
sudo chown www-data:www-data /run/gunicorn
```

3. Set up data directory:
```bash
sudo mkdir -p /home/flask/Hawaii_Cats/data
sudo chown www-data:www-data /home/flask/Hawaii_Cats/data
```

4. Start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hawaii-cats
sudo systemctl start hawaii-cats
sudo systemctl restart nginx
```

## Common Issues
1. Import Errors:
- Always use absolute imports starting with `app.`
- Example: `from app.tools.cat_simulation import DEFAULT_PARAMS`
- The PYTHONPATH is set to include both `/home/flask/Hawaii_Cats` and `/home/flask/Hawaii_Cats/app`

2. Firebase Issues:
- Ensure Firebase credentials are present at `/home/flask/Hawaii_Cats/app/firebase-credentials.json`
- The application will still work for non-Firebase functionality if credentials are missing
- Set `ENABLE_FIREBASE_SYNC=false` in `.env.local` to disable Firebase completely

3. Permission Issues:
- The gunicorn service runs as `www-data:www-data`
- Make sure `/run/gunicorn` and `/home/flask/Hawaii_Cats/data` are owned by `www-data`
- The socket file `/run/gunicorn/gunicorn.socket` should be owned by `www-data`

## Monitoring
- Check application logs: `sudo journalctl -u hawaii-cats`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Check service status: `sudo systemctl status hawaii-cats`
