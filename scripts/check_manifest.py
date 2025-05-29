#!/usr/bin/env python

import csv
import argparse
from textwrap import dedent
from pathlib import Path


def extract_filename(row: dict) -> str:
    """
    Extract the filename from the row.
    """
    forward_path = row["forward-absolute-filepath"]
    reverse_path = row["reverse-absolute-filepath"]
    forward_name = Path(forward_path).name
    reverse_name = Path(reverse_path).name
    return forward_name, reverse_name


def extract_first_underscore(string: str) -> str:
    """
    Extract the sample name from the row.
    """
    return string.replace(".fastq", "").replace(".gz", "").split("_")[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path",
        help=dedent(
            """
            Path of data, metadata or manifest
            """
        ),
    )

    manifest_path = parser.parse_args().input_path
    error_msg = ""
    with open(manifest_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            sample_id = row["sample-id"]
            forward_name, reverse_name = extract_filename(row)

            forward_sample = extract_first_underscore(forward_name)
            reverse_sample = extract_first_underscore(reverse_name)
            if forward_sample != reverse_sample:
                error_msg += f"id: {sample_id}, "
                error_msg += f"forward: ({forward_sample}) と "
                error_msg += f"reverse: ({reverse_sample}) が一致しません。\n"

    if error_msg != "":
        raise SyntaxError(error_msg)
