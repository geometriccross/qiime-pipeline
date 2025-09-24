from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Any
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


class RequiresDirectory:
    def __init__(self):
        self.__pathes: set[Path] = set()

    def __add__(self, other: RequiresDirectory):
        return self.__pathes.union(other.__pathes)

    def add(self, path: Path):
        self.__pathes.add(path)

    def ensure(self, executor: Executor):
        for path in self.__pathes:
            executor.run(["mkdir", "-p", path])


class Pipeline(ABC):
    @abstractmethod
    def __init__(self, context: PipelineContext):
        self.__context = context

    @abstractmethod
    def command_list(self) -> Tuple[Q2CmdAssembly, RequiresDirectory, Any[str]]: ...

    def run(self) -> Path:
        self.__context.executor.run(["bash", "-c", "apt update && apt upgrade -y"])
        self.__context.executor.run(
            ["mkdir", "-p", self.__context.setting.container_data.output_path.ctn_pos]
        )

        [self.__context.executor.run(cmd) for cmd in self.command_list().build_all()]
