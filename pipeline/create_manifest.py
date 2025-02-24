import argparse
from glob import glob
from pathlib import Path

root_dir = "."
id_prefix = "id"

parser = argparse.ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("-p", "--id_prefix", default=".")
parser.add_argument("-h", "--help")

fastq_pathes = glob(root_dir + "/**/*gz", recursive=True)
fastq_pathes = sorted(fastq_pathes, reverse=True)

id_index = 1
string = "sample-id, forward-absolute-filepath, reverse-absolute-filepath"
while len(fastq_pathes) > 0:
    forward = fastq_pathes.pop()
    reverse = fastq_pathes.pop()

    string += "\n"
    string += id_prefix + id_index.__str__() + ", "
    string += Path(forward).absolute().__str__() + ", "
    string += Path(reverse).absolute().__str__() + ", "

    id_index += 1

print(string)
