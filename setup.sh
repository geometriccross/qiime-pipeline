#!/bin/bash

env_name=$(cat environment.yml | grep -oP '(?<=name: ).*')
conda activate $env_name