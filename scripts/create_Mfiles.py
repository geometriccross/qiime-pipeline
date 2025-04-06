#!/usr/bin/env python

import re
import csv
import argparse
from textwrap import dedent
from glob import glob
from pathlib import Path, PurePath


# queryで渡されたidを持つfastqファイルを返す
def search_fastq(q: str, data: list[str]) -> tuple[str]:
    correct = []
    for d in data:
        file_name = PurePath(d).name
        if re.match(f"^{q.upper()}_", file_name.upper()):
            correct.append(d)

    # R1, R2以外に名前がかぶっているfastqファイルがあったら
    if len(correct) > 2:
        raise SyntaxError(dedent(f"""
            同名のファイルが3つ以上存在しています。\n
            {correct}
        """))

    fwd = list(filter(lambda s: s.__contains__("_R1_"), correct)).pop()
    rvs = list(filter(lambda s: s.__contains__("_R2_"), correct)).pop()

    fwd_abs_path = Path(fwd).absolute().__str__()
    rvs_abs_path = Path(rvs).absolute().__str__()
    return fwd_abs_path, rvs_abs_path


data_list = [
    {"meta": "/meta/bat_fleas.csv", "fastq": "/fastq/batfleas"},
    {"meta": "/meta/cat_fleas.csv", "fastq": "/fastq/catfleas"},
    {"meta": "/meta/lip_forti.csv", "fastq": "/fastq/sk"},
    {"meta": "/meta/mky_louse.csv", "fastq": "/fastq/monkeylice"}
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
# 適当なmetadataのヘッダーを取得
with Path(data_list[0]["meta"]).open() as f:
    header_str = f.readline().replace("\n", "")
    # csv writerowsで正常に書き込むためには二次元配列でなければならない
    master_list = [[
        id_prefix,
        *header_str.replace("#", "").replace("SampleID", "RawID").split(",")
    ]]

mani_result = []
mani_result.append([
    "sample-id",
    "forward-absolute-filepath",
    "reverse-absolute-filepath"
])

id_index = 1
for pair in data_list:
    fastq_pathes = glob(pair["fastq"] + "/**/*gz", recursive=True)
    with open(Path(pair["meta"]).absolute(), "r") as f:
        reader = csv.reader(f)
        header_removed = [row for row in reader][1:]
        for row in header_removed:
            # master csv
            master_list.append([
                id_prefix + id_index.__str__(),
                *row
            ])

            # manifest
            # 1列目にあるRawIDから対応するfastqファイルを取得
            mani_result.append([
                id_prefix + id_index.__str__(),
                *search_fastq(row[0], fastq_pathes)
            ])

            id_index += 1

with open(out_meta, "w") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(master_list)

with open(out_mani, "w") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(mani_result)
