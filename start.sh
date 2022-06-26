#!/bin/bash

while getopts ":a:p:" opt; do
  case $opt in
    p) project_name="$OPTARG"
    ;;
  esac
done

if [[ -z "$project_name" ]]
then
    echo "project name could not be empty"
    echo "help) -p <project_name>"
    exit 0
fi


PROJECT_NAME=$project_name

# create virtual environment
python3.9 -m venv .venv

# active environment
source .venv/bin/activate

# install requirements
pip install -r requirements.txt

CONFIG_PATH=$(pwd)/app.config
PYTHON_PATH=$(pwd)/.venv/bin/python3

tee /etc/systemd/system/$PROJECT_NAME.socket <<< "
[Unit]
Description = Backup from databases 
After = network.target
 
[Service]
Type = simple
ExecStart = $PYTHON_PATH main.py --action backup --configfile $CONFIG_PATH
Restart = on-failure # Restart when there are errors
 
[Install]
WantedBy = multi-user.target"
 
sudo systemctl daemon-reload
sudo systemctl enable $PROJECT_NAME.service
sudo systemctl start $PROJECT_NAME.service
