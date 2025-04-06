#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>
if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

