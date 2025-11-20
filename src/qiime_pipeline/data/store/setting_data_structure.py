import dataclasses
from pathlib import Path
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
class SettingData:
    container_data: ContainerData

    datasets: Datasets
    sampling_depth: int = 10000
    batch_id: str = dataclasses.field(default_factory=generate_id)

    def __post_init__(self):
        for p in filter(lambda item: isinstance(item, Path), self.__dict__.values()):
            assert p.exists(), f"Path {p} does not exist."
