#!/bin/bash

if [[ -z "${1}" ]]; then
	echo No input > /dev/stderr
fi

if [[ -z "${BROWSER}" ]]; then
	echo ENV BROWSER not set > /dev/stderr
fi
