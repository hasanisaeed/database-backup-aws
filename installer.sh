#!/bin/bash

# ANSI escape codes for text formatting and colors
BOLD="\033[1m"
RESET="\033[0m"
GREEN="\033[32m"
CYAN="\033[36m"

# Prompt the user for input
printf "${BOLD}${CYAN}Enter your username (leave empty to use the current user):${RESET} "
read -r YOUR_USERNAME
YOUR_USERNAME=${YOUR_USERNAME:-$USER} # Use the current user if no username provided

# Get the absolute path of the current folder
CURRENT_DIRECTORY=$(pwd)

# Change this name with your desired main module name
SCRIPT_NAME="scheduler.py"

printf "${BOLD}${CYAN}$SCRIPT_NAME${RESET} "

# Create the helper script to run the Python script with arguments
cat <<'EOF' >run_script.sh
#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run the Python script with command-line arguments
python scheduler.py --config-file=config.json --output-format=gz --send-via=scp

# Deactivate the virtual environment
deactivate
EOF

# Make the helper script executable
chmod +x run_script.sh

# Create the systemd service unit file
echo -e "[Unit]\nDescription=Scheduler Service\nAfter=network.target\n" >scheduler.service
echo -e "[Service]\nType=simple\nUser=$YOUR_USERNAME" >>scheduler.service
echo -e "WorkingDirectory=$CURRENT_DIRECTORY" >>scheduler.service
echo -e "ExecStart=/bin/bash -c './run_script.sh --config-file=config.json --output-format=gz --send-via=scp --remove-after-sending=false'" >>scheduler.service
echo -e "Restart=always\n" >>scheduler.service
echo -e "[Install]\nWantedBy=multi-user.target" >>scheduler.service
echo -e "Alias=scheduler.service\n" >>scheduler.service # Add an Alias for easy access to the service

# Move the service unit file to the systemd directory
sudo mv scheduler.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Create a virtual environment and install the required packages
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# Enable and start the service
sudo systemctl enable scheduler
sudo systemctl start scheduler

printf "${BOLD}${GREEN}\nService 'scheduler' has been started.${RESET}\n"

sudo systemctl status scheduler.service

