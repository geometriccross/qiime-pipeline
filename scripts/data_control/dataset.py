import dataclasses
import json
from pathlib import Path
from typing import Any


class DatasetEncoder(json.JSONEncoder):
    """カスタムJSONエンコーダー for Dataset/Databank"""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (Dataset, Databank)):
            return obj.to_dict()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


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

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換"""
        return {
            "name": self.name,
            "fastq_folder": self.fastq_folder,
            "metadata_path": self.metadata_path,
            "fastq_files": self.fastq_files,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """オブジェクトをJSON文字列に変換"""
        return json.dumps(self, cls=DatasetEncoder, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Dataset":
        """JSON文字列からDatasetオブジェクトを生成"""
        data = json.loads(json_str)
        return cls(
            name=data["name"],
            fastq_folder=Path(data["fastq_folder"]),
            metadata_path=Path(data["metadata_path"]),
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

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換"""
        return {"sets": self.sets}

    def to_json(self) -> str:
        """オブジェクトをJSON文字列に変換"""
        return json.dumps(self, cls=DatasetEncoder, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Databank":
        """JSON文字列からDatabankオブジェクトを生成"""
        data = json.loads(json_str)
        return cls(
            sets={Dataset.from_json(json.dumps(d, indent=2)) for d in data["sets"]}
        )
