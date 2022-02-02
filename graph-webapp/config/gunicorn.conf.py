bind = "0.0.0.0:5000"
#bind = "127.0.0.1:5000"
workers = 1  # only one worker per gunicorn instance when using async worker.
#worker_class = 'eventlet'  // not compatible with python 3.10?
timeout = 30  # 30 second request timeout
errorlog = "./logs/gunicorn_error.log"
accesslog = "./logs/gunicorn_access.log"
loglevel = "info"

