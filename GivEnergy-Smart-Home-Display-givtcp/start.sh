#!/bin/bash

# Get the current directory of the script
APPDIRECTORY=$(cd $(dirname $0) && pwd)

cd $APPDIRECTORY

# Serve the folder as a web server (default port is 3000)
serve &>/dev/null &