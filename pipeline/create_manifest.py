from sys import argv
from glob import glob
from pathlib import Path

root_dir = "."
id_prefix = "id"
# argv[0] are contained file name
if len(argv) > 1:
    root_dir = argv[1]
    id_prefix = argv[2]

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
