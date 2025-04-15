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
    "-c",
    "--column",
    default="0",
    help=dedent(
        """
        Target column
        """
    )
),
parser.add_argument(
    "-r",
    "--exclude",
    action="store_true",
    help=dedent("""
        """)
)

args = parser.parse_args()
# if targets passed like this, id1 id2 id3
# argparse convert like this
# [["i", "d", "1"], ["i", "d", "2"], ["i", "d", "3"]]
# so we need concatinate it
targets = []
for target in args.targets:
    targets.append("".join(target))

with open(args.input_path, newline="") as file:
    reader = csv.reader(file, delimiter="\t")
    header = next(reader)
    output_lines = ["\t".join(header)]
    for row in reader:
        # 列数が足りない行はスキップ
        if len(row) <= args.column:
            continue
        # 指定された列の値がターゲットに含まれているかどうか
        match = row[args.column] in args.targets
        if args.exclude:
            if not match:
                output_lines.append("\t".join(row))
        else:
            if match:
                output_lines.append("\t".join(row))

print("\n".join(output_lines))
