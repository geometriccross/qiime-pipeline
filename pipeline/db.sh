#!/bin/bash

CREATE_DB="${OUT}/dbgen_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
mkdir -p "${CREATE_DB}"

wget -P "${CREATE_DB}" https://data.qiime2.org/2024.10/common/silva-138-99-seqs.qza
wget -P "${CREATE_DB}" https://data.qiime2.org/2024.10/common/silva-138-99-tax.qza

qiime feature-classifier extract-reads \
	--p-min-length 350 \
	--p-max-length 500 \
	--p-f-primer CCTACGGGNGGCWGCAG \
	--p-r-primer GACTACHVGGGTATCTAATCC \
	--i-sequences "${CREATE_DB}/silva-138-99-seqs.qza" \
	--o-reads "${CREATE_DB}/ref-seqs-silva-138.qza"

qiime feature-classifier fit-classifier-naive-bayes \
	--i-reference-reads "${CREATE_DB}/ref-seqs-silva-138.qza" \
	--i-reference-taxonomy "${CREATE_DB}/silva-138-99-tax.qza" \
	--o-classifier "${CREATE_DB}/classifier-silva138.qza"

cp -f "${CREATE_DB}/classifier-silva138.qza" "${DB}/classifier.qza"
