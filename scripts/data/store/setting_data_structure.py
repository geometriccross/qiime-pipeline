import dataclasses
from pathlib import Path
from collections.abc import Mapping
import tomlkit
from tomlkit.toml_file import TOMLFile
from .dataset import Datasets
from .generate_id import generate_id


class PairPath:
    """
    ローカルのパスとDockerコンテナでのマウント先の組
    """

    def __init__(self, local_pos: Path, ctn_pos: Path):
        self.local_pos = local_pos
        self.ctn_pos = ctn_pos


@dataclasses.dataclass
class ContainerData:
    image_or_dockerfile: str | Path
    workspace_path: Path
    output_path: PairPath
    database_path: PairPath


@dataclasses.dataclass
class SettingData(Mapping):
    container_data: ContainerData

    datasets: Datasets
    sampling_depth: int = 10000
    batch_id: str = dataclasses.field(default_factory=generate_id)

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
