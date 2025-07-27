import dataclasses
from pathlib import Path
from collections.abc import Mapping
import tomlkit
from tomlkit.toml_file import TOMLFile
from ..data_control.dataset import Databank


@dataclasses.dataclass
class SettingData(Mapping):
    host_side_fastq_folder: Path
    container_side_fastq_folder: Path
    host_side_metadata_folder: Path
    container_side_metadata_folder: Path

    dockerfile: Path

    sampling_depth: int
    databank: Databank

    def __post_init__(self):
        for p in filter(lambda item: isinstance(item, Path), self.__dict__.values()):
            assert p.exists(), f"Path {p} does not exist."

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __iter__(self):
        return super().__iter__()

    def __len__(self):
        return super().__len__()

    def to_toml(self) -> tomlkit.TOMLDocument:
        doc = tomlkit.document()
        for key, value in self.__dict__.items():
            if hasattr(value, "to_toml"):
                doc.add(key, value.to_toml())
            elif isinstance(value, Path):
                doc.add(key, str(value.absolute()))
            else:
                doc.add(key, value)

        return doc

    def write(self, path: Path):
        """
        Write the setting data to a file-like object.
        """
        TOMLFile(path).write(self.to_toml())
