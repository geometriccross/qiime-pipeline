from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple
from scripts.data.store import SettingData
from .executor import Executor
from .qiime_command import Q2CmdAssembly


class PipelineContext:
    def __init__(
        self,
        ctn_metadata: Path,
        ctn_manifest: Path,
        executor: Executor,
        setting: SettingData,
    ):
        self.ctn_metadata: Path = ctn_metadata
        self.ctn_manifest: Path = ctn_manifest
        self.executor: Executor = executor
        self.setting: SettingData = setting


class Pipeline(ABC):
    @abstractmethod
    def __init__(self, context: PipelineContext):
        self.__context = context

    @abstractmethod
    def command_list(self) -> Tuple[Q2CmdAssembly, str]: ...

    def run(self) -> Path:
        self.__context.executor.run(["bash", "-c", "apt update && apt upgrade -y"])
        self.__context.executor.run(
            ["mkdir", "-p", self.__context.setting.container_data.output_path.ctn_pos]
        )

        [self.__context.executor.run(cmd) for cmd in self.command_list().build_all()]
