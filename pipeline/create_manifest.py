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
# argparse can automatically convert "-" into "_"
id_prefix = args.__dict__["id_prefix"]

fastq_pathes = glob(root_dir + "/**/*gz", recursive=True)
fastq_pathes = sorted(fastq_pathes, reverse=True)

id_index = 1
string = "sample-id\tforward-absolute-filepath\treverse-absolute-filepath"
while len(fastq_pathes) > 0:
    forward = fastq_pathes.pop()
    reverse = fastq_pathes.pop()

    string += "\n"
    string += id_prefix + id_index.__str__() + "\t"
    string += Path(forward).absolute().__str__() + "\t"
    string += Path(reverse).absolute().__str__() + "\t"

    id_index += 1

print(string)
