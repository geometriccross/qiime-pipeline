#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>
if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

CREATE_DB="/tmp/$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 5 | head -1)"
mkdir -p "${CREATE_DB}"
cd "$CREATE_DB" || exit 1

wget -P . https://data.qiime2.org/2024.10/common/silva-138-99-seqs.qza
wget -P . https://data.qiime2.org/2024.10/common/silva-138-99-tax.qza

qiime feature-classifier extract-reads \
	--p-min-length 350 \
	--p-max-length 500 \
	--p-f-primer CCTACGGGNGGCWGCAG \
	--p-r-primer GACTACHVGGGTATCTAATCC \
	--i-sequences silva-138-99-seqs.qza \
	--o-reads ref-seqs-silva-138.qza

qiime feature-classifier fit-classifier-naive-bayes \
	--i-reference-reads ref-seqs-silva-138.qza \
	--i-reference-taxonomy silva-138-99-tax.qza \
	--o-classifier classifier-silva138.qza

realpath classifier-silva138.qza
