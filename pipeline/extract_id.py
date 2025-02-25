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
    nargs="*",
    help=dedent(
        """
        Id that would extract id
        """
    )
)
parser.add_argument(
    "-r",
    "--reverse",
    action="store_false",
    help=dedent(
        """
        If you specify this TRUE, The data with the passed id removed is output
        """
    )
)

args = parser.parse_args()
# if targets passed like this, id1 id2 id3
# argparse convert like this
# [["i", "d", "1"], ["i", "d", "2"], ["i", "d", "3"]]
# so we need concatinate it
targets = []
for target in args.targets:
    targets.append("".join(target))

with open(args.input_path, "r") as file:
    reader = csv.reader(file, delimiter="\t")

    result = ""
    reverse = ""
    for row in reader:
        if row[0] in targets:
            reverse += "\t".join(row) + "\n"
        else:
            result += "\t".join(row) + "\n"

    if args.reverse:
        print(reverse)
    else:
        print(result)
