#!/bin/bash

###############################################################################
# Auto-generated by qiime2 v.2024.10.1 at 11:29:59 PM on 27 Feb, 2025
# This document is a representation of the scholarly work of the creator of the
# QIIME 2 Results provided as input to this software, and may be protected by
# intellectual property law. Please respect all copyright restrictions and
# licenses governing the use, modification, and redistribution of this work.

# For User Support, post to the QIIME2 Forum at https://forum.qiime2.org.

# Instructions for use:
# 1. Open this script in a text editor or IDE. Support for BASH
#    syntax highlighting can be helpful.
# 2. Search or scan visually for '<' or '>' characters to find places where
#    user input (e.g. a filepath or column name) is required. These must be
#    replaced with your own values. E.g. <column name> -> 'patient_id'.
#    Failure to remove '<' or '>' may result in `No such File ...` errors
# 3. Search for 'FIXME' comments in the script, and respond as directed.
# 4. Remove all 'FIXME' comments from the script completely. Failure to do so
#    may result in 'Missing Option' errors
# 5. Adjust the arguments to the commands below to suit your data and metadata.
#    If your data is not identical to that in the replayed analysis,
#    changes may be required. (e.g. sample ids or rarefaction depth)
# 6. Optional: replace any filenames in this script that begin with 'XX' with
#    unique file names to ensure they are preserved. QIIME 2 saves all outputs
#    from all actions in this script to disk regardless of whether those
#    outputs were in the original collection of replayed results. The filenames
#    of "un-replayed" artifacts are prefixed with 'XX' so they may be easily
#    located. These names are not guaranteed to be unique, so 'XX_table.qza'
#    may be overwritten by another 'XX_table.qza' later in the script.
# 7. Activate your replay conda environment, and confirm you have installed all
#    plugins used by the script.
# 8. Run this script with `bash <path to this script>`, or copy-paste commands
#    into the terminal for a more interactive analysis.
# 9. Optional: to delete all results not required to produce the figures and
#    data used to generate this script, navigate to the directory in which you
#    ran the script and `rm XX*.qz*`
###############################################################################
## function to create result collections ##
construct_result_collection () {
	mkdir $rc_name
	touch $rc_name.order
	for key in "${keys[@]}"; do
		echo $key >> $rc_name.order
	done
	for i in "${!keys[@]}"; do
		ln -s ../"${names[i]}" $rc_name"${keys[i]}"$ext
	done
}
##

# This tells bash to -e exit immediately if a command fails
# and -x show all commands in stdout so you can track progress
set -e -x

qiime rescript get-silva-data \
  --p-version 138.2 \
  --p-target SSURef_NR99 \
  --p-include-species-labels \
  --p-rank-propagation \
  --p-download-sequences \
  --o-silva-taxonomy silva-taxonomy-0.qza \
  --o-silva-sequences silva-sequences-0.qza

qiime rescript cull-seqs \
  --i-sequences silva-sequences-0.qza \
  --p-num-degenerates 5 \
  --p-homopolymer-length 8 \
  --p-n-jobs 8 \
  --o-clean-sequences clean-sequences-0.qza

qiime rescript filter-seqs-length-by-taxon \
  --i-sequences clean-sequences-0.qza \
  --i-taxonomy silva-taxonomy-0.qza \
  --p-labels Archaea Bacteria Eukaryota \
  --p-min-lens 900 1200 1400 \
  --o-filtered-seqs filtered-seqs-0.qza \
  --o-discarded-seqs XX_discarded_seqs

qiime rescript dereplicate \
  --i-sequences filtered-seqs-0.qza \
  --i-taxa silva-taxonomy-0.qza \
  --p-mode uniq \
  --p-perc-identity 1.0 \
  --p-threads 8 \
  --p-rank-handles domain phylum class order family genus species \
  --p-no-derep-prefix \
  --o-dereplicated-taxa dereplicated-taxa-0.qza \
  --o-dereplicated-sequences dereplicated-sequences-0.qza

qiime feature-classifier extract-reads \
  --i-sequences dereplicated-sequences-0.qza \
  --p-f-primer ACTCCTACGGGAGGCAGCAG \
  --p-r-primer GGACTACHVGGGTWTCTAAT \
  --p-trim-right 0 \
  --p-trunc-len 0 \
  --p-trim-left 0 \
  --p-identity 0.8 \
  --p-min-length 50 \
  --p-max-length 0 \
  --p-n-jobs 8 \
  --p-batch-size auto \
  --p-read-orientation forward \
  --o-reads reads-0.qza

qiime rescript dereplicate \
  --i-sequences reads-0.qza \
  --i-taxa dereplicated-taxa-0.qza \
  --p-mode uniq \
  --p-perc-identity 1.0 \
  --p-threads 8 \
  --p-rank-handles domain phylum class order family genus species \
  --p-no-derep-prefix \
  --o-dereplicated-sequences dereplicated-sequences-1.qza \
  --o-dereplicated-taxa dereplicated-taxa-1.qza

qiime feature-classifier fit-classifier-naive-bayes \
  --i-reference-reads dereplicated-sequences-1.qza \
  --i-reference-taxonomy dereplicated-taxa-1.qza \
  --p-classify--alpha 0.001 \
  --p-classify--chunk-size 20000 \
  --p-classify--class-prior null \
  --p-no-classify--fit-prior \
  --p-no-feat-ext--alternate-sign \
  --p-feat-ext--analyzer char_wb \
  --p-no-feat-ext--binary \
  --p-feat-ext--decode-error strict \
  --p-feat-ext--encoding utf-8 \
  --p-feat-ext--input content \
  --p-feat-ext--lowercase \
  --p-feat-ext--n-features 8192 \
  --p-feat-ext--ngram-range '[7, 7]' \
  --p-feat-ext--norm l2 \
  --p-feat-ext--preprocessor null \
  --p-feat-ext--stop-words null \
  --p-feat-ext--strip-accents null \
  --p-feat-ext--token-pattern '(?u)\b\w\w+\b' \
  --p-feat-ext--tokenizer null \
  --p-no-verbose \
  --o-classifier classifier-0.qza


###############################################################################
# The following QIIME 2 Results were parsed to produce this script:
# db4a499c-e5d7-4dd2-81e9-b5d6c14a65aa
###############################################################################
