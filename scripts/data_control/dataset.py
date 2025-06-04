import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Dataset:
    """
    A class to represent a dataset.
    """

    name: str
    fastq_path: Path
    metadata_path: Path

    def __post_init__(self):
        if not self.fastq_path.exists():
            raise FileNotFoundError(f"Fastq path {self.fastq_path} does not exist.")
        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata path {self.metadata_path} does not exist."
            )


@dataclasses.dataclass
class Databank:
    """
    A class to represent a dataset.
    """

    sets: set[Dataset]

    def __post_init__(self):
        for dataset in self.sets:
            # add attribute
            self.__dict__[dataset.name] = dataset
