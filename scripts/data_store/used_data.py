import docker
from pathlib import Path
from .dataset import Dataset, Datasets
from .container import provid_container, mounts
from .ribosome_regions import V3V4


def used_data(
    container_side_fastq_stored_path: Path, container_side_meta_stored_path: Path
) -> Datasets:
    __bat_fleas = Dataset(
        name="bat_fleas",
        fastq_folder=container_side_fastq_stored_path.joinpath("/batfleas"),
        metadata_path=container_side_meta_stored_path.joinpath("/bat_fleas.csv"),
        region=V3V4,
    )

    __cat_fleas = Dataset(
        name="cat_fleas",
        fastq_folder=container_side_fastq_stored_path.joinpath("/catfleas"),
        metadata_path=container_side_meta_stored_path.joinpath("/cat_fleas.csv"),
        region=V3V4,
    )

    __deer_keds = Dataset(
        name="deer_keds",
        fastq_folder=container_side_fastq_stored_path.joinpath("/deerkeds"),
        metadata_path=container_side_meta_stored_path.joinpath("/deer_keds.csv"),
        region=V3V4,
    )

    __mk_louses = Dataset(
        name="mk_louses",
        fastq_folder=container_side_fastq_stored_path.joinpath("/mklouses"),
        metadata_path=container_side_meta_stored_path.joinpath("/mk_louses.csv"),
        region=V3V4,
    )

    return Datasets(
        sets=[
            __bat_fleas,
            __cat_fleas,
            __deer_keds,
            __mk_louses,
        ]
    )


def used_container(dockerfile: Path, data_folder: Path) -> str:
    """
    Build and run a Docker container for the QIIME pipeline.

    Args:
        dockerfile (Path): Path to the Dockerfile for building the container.

    Returns:
        str: Name of the running container.
    """

    pipeline_ctn: docker.models.containers.Container = provid_container(dockerfile)
    pipeline_ctn.mounts = mounts(
        data_path=data_folder
    )  # Assuming the data path is set to /data in the container
    return pipeline_ctn.name
