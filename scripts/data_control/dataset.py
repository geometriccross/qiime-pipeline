from __future__ import annotations
import dataclasses
import json
from pathlib import Path
import tomlkit
from .ribosome_regions import Region


@dataclasses.dataclass
class Dataset:
    """
    A class to represent a dataset.
    """

    name: str
    fastq_folder: Path
    metadata_path: Path
    region: Region

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

    def to_toml(self) -> tomlkit.TOMLDocument:
        """
        Convert the dataset to a TOML document.
        """
        doc = tomlkit.document()
        doc.add("name", self.name)
        doc.add("fastq_folder", str(self.fastq_folder))
        doc.add("metadata_path", str(self.metadata_path))
        doc.add("region", self.region.to_toml())
        return doc

    @classmethod
    def from_toml(cls, toml_doc: tomlkit.TOMLDocument) -> "Dataset":
        """
        Create a Dataset instance from a TOML document.
        """
        return Dataset(
            name=toml_doc["name"],
            fastq_folder=Path(toml_doc["fastq_folder"]),
            metadata_path=Path(toml_doc["metadata_path"]),
            region=Region.from_toml(toml_doc["region"]),
        )

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換"""
        return {
            "name": self.name,
            "fastq_folder": self.fastq_folder,
            "metadata_path": self.metadata_path,
            "fastq_files": self.fastq_files,
            "metadata": self.metadata,
            "region": self.region.to_dict(),
        }


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

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換"""
        return {"sets": self.sets}
