pythonpath = '/home/flask/Hawaii_Cats'
bind = 'unix:/home/flask/Hawaii_Cats/gunicorn.socket'
workers = 3
worker_class = 'gevent'
timeout = 120
keepalive = 65
preload_app = True
chdir = '/home/flask/Hawaii_Cats'
user = 'flask'
group = 'www-data'
env = {
    'PYTHONPATH': '/home/flask/Hawaii_Cats',
    'FLASK_ENV': 'production',
    'FLASK_APP': 'wsgi:app'
}
accesslog = '/home/flask/Hawaii_Cats/logs/access.log'
errorlog = '/home/flask/Hawaii_Cats/logs/gunicorn.log'
loglevel = 'debug'
