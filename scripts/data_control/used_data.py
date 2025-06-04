from pathlib import Path
from dataset import Dataset, Databank

__bat_fleas = Dataset(
    name="bat_fleas",
    fastq_folder=Path("/fastq/batfleas"),
    metadata_path=Path("/meta/bat_fleas.csv"),
)

__cat_fleas = Dataset(
    name="cat_fleas",
    fastq_folder=Path("/fastq/catfleas"),
    metadata_path=Path("/meta/cat_fleas.csv"),
)

__deer_keds = Dataset(
    name="deer_keds",
    fastq_folder=Path("/fastq/deerkeds"),
    metadata_path=Path("/meta/deer_keds.csv"),
)

__mk_louses = Dataset(
    name="mk_louses",
    fastq_folder=Path("/fastq/mklouses"),
    metadata_path=Path("/meta/mk_louses.csv"),
)

databank = Databank(
    sets=[
        __bat_fleas,
        __cat_fleas,
        __deer_keds,
        __mk_louses,
    ]
)
