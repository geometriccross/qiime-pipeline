#!/usr/bin/env python

import csv
import argparse
from textwrap import dedent
from validate_pattern import validate_pattern, extract_pattern


def raise_err(id: str, forward: str, reverse: str) -> str:
    msg = f"id: {id}, forward: ({forward}) と reverse: ({reverse}) が一致しません。\n"
    raise SyntaxError(msg)


def check_manifest(manifest_path: str) -> bool:
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
