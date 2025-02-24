import csv
import argparse
from textwrap import dedent
from glob import glob
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "input_path",
    default=".",
    help=dedent(
        """
        path of fastq containered
        """
    )
)
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

args = parser.parse_args()
root_dir = args.__dict__["input_path"]
id_prefix = args.__dict__["id_prefix"]

csv_pathes = glob(root_dir + "/**/*csv", recursive=True)

csvs = []
try:
    csvs = [open(Path(file).absolute(), "r") for file in csv_pathes]
    readers = [csv.reader(obj) for obj in csvs]

    # Get header and restore the moved seek
    master_header = csvs[0].readline().replace("\n", "")
    master_header = [
        id_prefix,
        *master_header.replace("#", "").replace("SampleID", "RawID").split(",")
    ]
    csvs[0].seek(0)

    master_list = []
    id_idex = 1
    for reader in readers:
        header_removed = [row for row in reader][1:]
        for row in header_removed:
            master_list.append([
                id_prefix + id_idex.__str__(),
                *row
            ])
            id_idex += 1

    print(",".join(master_header))
    for row in master_list:
        print(",".join(row))

finally:
    for opened in csvs:
        opened.close()
