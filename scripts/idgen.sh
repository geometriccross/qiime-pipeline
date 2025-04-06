#!/bin/bash

month="$(date +%b | tr '[:upper:]' '[:lower:]')"
random="$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 3 | head -1 | tr '[:upper:]' '[:lower:]')"

echo "$month$(date +%d%H%M%S)_$random"
