from __future__ import annotations
from abc import ABC
from pathlib import Path
from src.data.store import SettingData
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
        new_requires = RequiresDirectory()
        new_requires.__pathes = self.__pathes.union(other.__pathes)
        return new_requires

    def add(self, path: Path):
        self.__pathes.add(path)

    def ensure(self, executor: Executor):
        for path in self.__pathes:
            executor.run(["mkdir", "-p", path])


class Pipeline(ABC):
    def __init__(self, context: PipelineContext, ctn_output: str = None):
        self._context = context
        self._assembly = Q2CmdAssembly()
        self._requires = RequiresDirectory()
        self._result = {}

        if ctn_output is None:
            self._output = self._context.setting.container_data.output_path.ctn_pos

        self._requires.add(self._output)

    def __call__(
        self,
        inputs: dict[str] = None,
    ):
        """Only return the result without execution. This is a dry run."""
        return self._result

    def __add__(self, other: Pipeline) -> Pipeline:
        self_result = self._cmd_build()
        other_result = other._cmd_build(self_result)  #

        new_pipeline = Pipeline(self._context)
        new_pipeline._assembly = self._assembly + other._assembly
        new_pipeline._requires = self._requires + other._requires
        new_pipeline._result = {**self_result, **other_result}

        self._assembly.sort_commands()
        return new_pipeline

    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]: ...

    def run(self):
        self._requires.ensure(self._context.executor)
        for cmd in self._assembly.build_all():
            self._context.executor.run(cmd)
