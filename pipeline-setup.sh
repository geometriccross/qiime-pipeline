#!/bin/bash

# check and install conda
which conda > /dev/null
if [ $? -ne 0 ]; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    rm ~/miniconda.sh
    source ~/miniconda/bin/activate
fi

# check and install mamba
which mamba > /dev/null
if [ $? -ne 0 ]; then
    conda install -q -y -c conda-forge mamba
fi

env_file=${1:-environment.yml}
if [ ! -e "$env_file" ]; then
    echo environment file is not exist.
    exit 1
fi

# get environment name
env_name=$(cat $env_file | grep -oP '(?<=name: ).*')
if [ -z "$env_name" ]; then
    echo echo "Error: Could not find environment name in '$env_file'"
fi

if [[ `mamba env list` =~ "qiime-pipeline" ]]; then
    mamba env update -q -n "$env_name" -f $env_file
else
    mamba env create -q -n "$env_name" -f $env_file
fi

mamba init
source ~/.bashrc && source ~/.zshrc
mamba activate "$env_name"
