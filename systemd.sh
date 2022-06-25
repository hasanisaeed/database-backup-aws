echo 
"
[Unit]
Description = Backup from databases 
After = network.target
 
[Service]
Type = simple
ExecStart = python <Path of the script you want to run>
User = root
Group = root
Restart = on-failure # Restart when there are errors
 
[Install]
WantedBy = multi-user.target

" > /etc/systemd/system/$PROJECT_NAME.socket