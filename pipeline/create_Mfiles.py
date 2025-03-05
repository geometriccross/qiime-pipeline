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

id_prefix = parser.parse_args().id_prefix,
master_header = data_list[0]["meta"].readline().replace("\n", "")
master_header = [
    id_prefix,
    *master_header.replace("#", "").replace("SampleID", "RawID").split(",")
]
data_list[0]["meta"].seek(0)

id_index = 1
mani_result = "sample-id\tforward-absolute-filepath\treverse-absolute-filepath"
master_list = []
for pair in data_list:
    pre_indexer = id_index
    # create manifest
    fastq_pathes = glob(pair["fastq"], "/**/*gz", recursive=True)
    while len(fastq_pathes) > 0:
        forward = fastq_pathes.pop()
        reverse = fastq_pathes.pop()

        mani_result += "\n"
        mani_result += id_prefix + id_index.__str__() + "\t"
        mani_result += Path(forward).absolute().__str__() + "\t"
        mani_result += Path(reverse).absolute().__str__() + "\t"

        id_index += 1

    # reset index
    id_index = pre_indexer
    # create csv
    with open(Path(pair["meta"]).absolute(), "r") as f:
        reader = csv.reader(f)
        header_removed = [row for row in reader][1:]
        for row in header_removed:
            master_list.append([
                id_prefix + id_index.__str__(),
                *row
            ])
            id_index += 1

