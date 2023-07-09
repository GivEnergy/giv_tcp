#!/bin/bash

# Get the current directory of the script
APPDIRECTORY=$(cd $(dirname $0) && pwd)

# Install "unclutter" - this enables the auto-hiding of the mouse cursor after a certain period of inactivity
apt-get install unclutter -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y

# Install "serve" - this enables serving the web app in the current directory on the Pi and local network
npm install -g serve

# Add a new cron job to run the app startup script on each reboot
# This starts the web server in the current directory, allowing Chromium
# to run the app.
echo "Adding new cron job for app in: ${APPDIRECTORY}"
(crontab -l 2>/dev/null; echo "@reboot ${APPDIRECTORY}/start.sh") | crontab -

echo " "
echo "Please remember to populate your Home Assistant access token in 'app.json', and set the base domain if it's different."