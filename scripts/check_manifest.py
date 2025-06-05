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


def modify_row(row: dict) -> tuple:
    """
    Modify the row to include the sample name.
    """
    forward_name, reverse_name = extract_filename(row)
    forward_sample = extract_first_underscore(forward_name)
    reverse_sample = extract_first_underscore(reverse_name)
    return forward_sample, reverse_sample


def raise_err(id: str, forward: str, reverse: str) -> str:
    msg = f"id: {id}, forward: ({forward}) と reverse: ({reverse}) が一致しません。\n"
    raise SyntaxError(msg)


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
            forward_sample, reverse_sample = modify_row(row)

            if forward_sample != reverse_sample:
                raise_err(row["id"], forward_sample, reverse_sample)
