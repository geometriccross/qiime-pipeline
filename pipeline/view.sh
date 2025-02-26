#!/bin/bash

if [[ -z "${WSL_DISTRO_NAME}" ]]; then
	echo Not in WSL >/dev/stderr
fi

if [[ -z "${1}" ]]; then
	echo No input >/dev/stderr
fi

if [[ -z "${BROWSER}" ]]; then
	echo ENV BROWSER not set >/dev/stderr
fi
