import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Dataset:
    """
    A class to represent a dataset.
    """

    name: str
    fastq_folder: Path
    metadata_path: Path

    def __get_fastq_files(self, fastq_folder: Path) -> list[Path]:
        return [
            *list(fastq_folder.glob("*.fastq")),
            *list(fastq_folder.glob("*.fastq.gz")),
        ]

    def __get_metadata(self) -> list[str]:
        with self.metadata_path.open() as f:
            return f.readlines()

    def __post_init__(self):
        if not self.fastq_folder.exists():
            raise FileNotFoundError(f"Fastq path {self.fastq_folder} does not exist.")
        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata path {self.metadata_path} does not exist."
            )

        self.fastq_files = self.__get_fastq_files(self.fastq_folder)
        self.metadata = self.__get_metadata()

    def __hash__(self):
        return hash((self.name, self.fastq_folder, self.metadata_path))


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
