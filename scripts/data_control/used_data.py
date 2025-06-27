from pathlib import Path
from .dataset import Dataset, Databank


def used_data(
    container_side_fastq_stored_path: Path, container_side_meta_stored_path: Path
) -> Databank:
    __bat_fleas = Dataset(
        name="bat_fleas",
        fastq_folder=container_side_fastq_stored_path.joinpath("/batfleas"),
        metadata_path=container_side_meta_stored_path.joinpath("/bat_fleas.csv"),
    )

    __cat_fleas = Dataset(
        name="cat_fleas",
        fastq_folder=container_side_fastq_stored_path.joinpath("/catfleas"),
        metadata_path=container_side_meta_stored_path.joinpath("/cat_fleas.csv"),
    )

    __deer_keds = Dataset(
        name="deer_keds",
        fastq_folder=container_side_fastq_stored_path.joinpath("/deerkeds"),
        metadata_path=container_side_meta_stored_path.joinpath("/deer_keds.csv"),
    )

    __mk_louses = Dataset(
        name="mk_louses",
        fastq_folder=container_side_fastq_stored_path.joinpath("/mklouses"),
        metadata_path=container_side_meta_stored_path.joinpath("/mk_louses.csv"),
    )

    return Databank(
        sets=[
            __bat_fleas,
            __cat_fleas,
            __deer_keds,
            __mk_louses,
        ]
    )
