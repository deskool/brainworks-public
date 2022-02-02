#!/usr/bin/env bash

# ensure the CWD is the directory of this script
script_dir="$(dirname $(realpath $0))"
cd $script_dir

cd ../  # move to main directory

# set up cronjob to check server status
script_path="$(pwd -P)/scripts/check_server_status.sh"  # get absolute path of script
(sudo crontab -l ; echo "* * * * * ${script_path}") 2>/dev/null | sort | uniq | sudo crontab -

