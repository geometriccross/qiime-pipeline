#!/bin/bash

tmp="out/$(sha256sum <(date) | cut -d ' ' -f 1)"
export OUT="${tmp}"
unset tmp

export DATA_SOURCE="fastq"
export META_SOURCE="meta"
export MANI="${OUT}/manifest.csv"
export META="${OUT}/meta.csv"
