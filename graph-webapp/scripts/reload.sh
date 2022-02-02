#!/usr/bin/env bash

# ensure the CWD is the directory of this script
script_dir="$(dirname $(realpath $0))"
cd $script_dir

sudo pkill -HUP -f gunicorn

