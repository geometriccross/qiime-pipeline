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
parser.add_argument(
    "--out-meta",
    help=dedent(
        """
        output path to metadata
        """
    ).strip()
)
parser.add_argument(
    "--out-mani",
    help=dedent(
        """
        output path to manifest file
        """
    ).strip()
)

# 引数から取得
id_prefix = parser.parse_args().id_prefix
out_meta = parser.parse_args().out_meta
out_mani = parser.parse_args().out_mani

master_list = []
# metadataのヘッダーを取得
tmp_meta = data_list[0]["meta"]
with Path(tmp_meta).open() as f:
    header_str = f.readline().replace("\n", "")
    # csv writerowsで正常に書き込むためには二次元配列でなければならない
    master_list = [[
        id_prefix,
        *header_str.replace("#", "").replace("SampleID", "RawID").split(",")
    ]]

id_index = 1
mani_result = []
mani_result.append([
    "sample-id",
    "forward-absolute-filepath",
    "reverse-absolute-filepath"
])

for pair in data_list:
    pre_indexer = id_index
    # create manifest
    fastq_pathes = glob(pair["fastq"] + "/**/*gz", recursive=True)
    while len(fastq_pathes) > 0:
        forward = fastq_pathes.pop()
        reverse = fastq_pathes.pop()

        row = []
        row.append(id_prefix + id_index.__str__())
        row.append(Path(forward).absolute().__str__())
        row.append(Path(reverse).absolute().__str__())
        mani_result.append(row)

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

with open(out_meta, "w") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(master_list)

with open(out_mani, "w") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(mani_result)
