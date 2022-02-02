#!/usr/bin/env bash

# ensure the CWD is the directory of this script
script_dir="$(dirname $(realpath $0))"
cd $script_dir

bash quit.sh
cd ../  # move to main directory

# start redis server for Flask session store
# redis-server config/session_redis.conf

# Run Nginx with custom config (needs absolute path to config)
# sudo nginx -c nginx.conf

# activate virtual environment
. venv/bin/activate

# call gunicorn with config file and log file
gunicorn -c config/gunicorn.conf.py "app:create_app()" &

