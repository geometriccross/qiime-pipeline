#!/bin/bash

tmp="out/$(sha256sum <(date) | cut -d ' ' -f 1)"
export OUT="${tmp}"
unset tmp

export DATA_SOURCE="fastq"
export META_SOURCE="meta"
export MANI="${OUT}/manifest.csv"
export META="${OUT}/meta.csv"

python pipeline/create_manifest.py "${DATA_SOURCE}" > "${MANI}"
python pipeline/create_master_csv.py "${META_SOURCE}" > "${META}"
