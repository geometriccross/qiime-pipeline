#!/usr/bin/env python

import csv
import argparse
from textwrap import dedent
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "input_path",
    help=dedent(
        """
        Path of data, metadata or manifest
        """
    )
)

manifest_path = parser.parse_args().input_path
error_msg = ""
with open(manifest_path, "r") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        sample_id = row["sample-id"]
        forward_path = row["forward-absolute-filepath"]
        reverse_path = row["reverse-absolute-filepath"]
        # ファイル名のみを抽出
        forward_name = Path(forward_path).name
        reverse_name = Path(reverse_path).name

        # 最初のアンダースコアまでの部分を抽出
        forward_sample = forward_name.split("_")[0]
        reverse_sample = reverse_name.split("_")[0]
        if forward_sample != reverse_sample:
            error_msg += f"id: {sample_id}, "
            error_msg += f"forward: ({forward_sample}) と "
            error_msg += f"reverse: ({reverse_sample}) が一致しません。\n"

if error_msg != "":
    raise SyntaxError(error_msg)
