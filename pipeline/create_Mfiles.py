#!/usr/bin/env python

import csv
import argparse
from textwrap import dedent
from glob import glob
from pathlib import Path

data_list = [
    {"meta": "meta/bat_fleas.csv", "fastq": "fastq/batfleas"},
    {"meta": "meta/cat_fleas.csv", "fastq": "fastq/catfleas"},
    {"meta": "meta/lip_cervi.csv", "fastq": "fastq/sk"},
    {"meta": "meta/mky_louse.csv", "fastq": "fastq/monkeylice"}
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--id-prefix",
    default="id",
    help=dedent(
        """
        set prefix id of each sample like this [REPLACE THIS] + numeric
        (default : %(default)s))
        """
    ).strip()
)

master_header = data_list[0]["meta"].readline().replace("\n", "")
master_header = [
    parser.parse_args().id_prefix,
    *master_header.replace("#", "").replace("SampleID", "RawID").split(",")
]
data_list[0]["meta"].seek(0)
