#!/usr/bin/env python

import csv
import argparse
from textwrap import dedent
from pathlib import Path, PurePath


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


def extract_pattern(row: dict) -> tuple[str, str]:
    """
    Extract the forward and reverse file names from the row.
    """
    forward_path = row["forward-absolute-filepath"]
    reverse_path = row["reverse-absolute-filepath"]
    forward_name = PurePath(forward_path).name
    reverse_name = PurePath(reverse_path).name
    return forward_name, reverse_name


def validate_pattern(forward: str, reverse: str) -> bool:
    """
    Validate the forward and reverse_name)
    return forward_sample, reverse_sample


def raise_err(id: str, forward: str, reverse: str) -> str:
    msg = f"id: {id}, forward: ({forward}) と reverse: ({reverse}) が一致しません。\n"
    raise SyntaxError(msg)


def check_manifest(manifest_path: str) -> True:
    """
    Check the manifest file for consistency.
    """
    with open(manifest_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            forward, reverse = extract_pattern(row)
            if not validate_pattern(forward, reverse):
                return False

    return True


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
    check_manifest(manifest_path)
