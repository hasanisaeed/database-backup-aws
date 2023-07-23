Automatic and adjustable backup of the database on AWS or anywhere else!

### Usage:

#### Run the script without a service:

    python scheduler.py --config-file=config.json --output-format=gz --send-via=scp --remove-after-sending=false

#### Run script as a service:

To run the script as a service and daemon on Unix-based systems (e.g., Linux), you can create a systemd service. Systemd
is a system and service manager that provides a standard way to manage services in modern Linux distributions. Here's
how you can create a systemd service for your Python script:
First of all save your Python script as scheduler.py or any desired filename.

1) Create a systemd service unit file with the following content. Replace ``/path/to/your/scheduler.py`` with the actual path
   to your Python script:

```bash
# /etc/systemd/system/scheduler.service
[Unit]
Description=Scheduler Service
After=network.target

[Service]
Type=simple
User=<your_username>  ; Replace with your username
WorkingDirectory=/path/to/your/directory   ; Replace with the directory containing the Python script
ExecStart=/usr/bin/python3 /path/to/your/scheduler.py   ; Replace with the correct path to the Python interpreter and your script
Restart=always

[Install]
WantedBy=multi-user.target
```

2) Save the file and reload the systemd daemon to pick up the new service:

```bash
sudo systemctl daemon-reload
```

3) Enable and start the service:

```bash
sudo systemctl enable scheduler
sudo systemctl start scheduler
```

4) Now, your Python script will run as a service and daemon, executing the my_task() function every 5 seconds. The
   service will start automatically on system boot and restart in case of any failures.

To check the status of the service:

```bash
sudo systemctl status scheduler
```

To stop the service:

```bash
sudo systemctl stop scheduler
```

To disable the service:

```bash 
sudo systemctl disable scheduler
```
