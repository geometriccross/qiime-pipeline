import csv
import argparse
from textwrap import dedent

parser = argparse.ArgumentParser()
parser.add_argument(
    "input_path",
    help=dedent(
        """
        Path of data, metadata or manifest
        """
    )
)
parser.add_argument(
    "targets",
    type=list,
    help=dedent(
        """
        Id that would extract id
        """
    )
)
parser.add_argument(
    "-r",
    "--reverse",
    default=False,
    type=bool,
    help=dedent(
        """
        If you specify this TRUE, The data with the passed id removed is output
        """
    )
)

args = parser.parse_args()
with open(args.input_path, "r") as file:
    reader = csv.reader(file, delimiter="\t")

    result = ""
    for row in reader:
        if row[0] in args.targets:
            continue

        result += "\t".join(row)

    print(result)
