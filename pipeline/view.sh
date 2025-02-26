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

dest="/tmp/$(date +%s | sha256sum | base64 | head -c 32)"
win_path=$(unzip -o "${1}" -d "${dest}" |
	sed "s/  inflating: //g" |
	grep data/index.html |
	xargs wslpath -w)

