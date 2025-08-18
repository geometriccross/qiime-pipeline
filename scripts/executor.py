from python_on_whales import docker, exceptions
from python_on_whales import Container
from pathlib import Path
from typing import Iterable, List


class Provider:
    def __init__(
        self,
        image: str,
        mounts: Iterable[List[str]] = (),
        workspace: Path = Path("."),
        remove=True,
    ):
        self.__image = docker.image.pull(image)
        self.__container = docker.container.run(
            image=self.__image,
            mounts=mounts,
            workdir=workspace.absolute(),
            command=["tail", "-f", "/dev/null"],
            detach=True,
            remove=remove,
        )

    def provide(self) -> Container:
        return self.__container

    @classmethod
    def get_status(cls, ctn: Container) -> str:
        """
        渡されたコンテナの状態を取得し、以下の結果が返される

        running: コンテナが実行中\n
        exited: コンテナが停止中\n
        absent: コンテナが存在しない
        """
        try:
            ctn.reload()
        except exceptions.NoSuchContainer:
            return "absent"

        # ContainerStateオブジェクトからstatusのみを選択する
        return ctn.state.status


class Executor:
    def __init__(self, container: Container):
        self.__container = container

    def __enter__(self):
        """コンテナの起動"""
        return CommandRunner(
            self.__container,
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテナの停止"""
        try:
            self.__container.stop()
        except exceptions.NoSuchContainer:
            pass

    def status(self) -> str:
        """コンテナのステータスを取得"""
        self.__container.reload()
        return self.__container.status


class CommandRunner:
    def __init__(self, container: Container):
        self.__container = container

    def run(self, command: str) -> tuple[str, str]:
        """
        以下のような形式でcommandを受け取り、実行する

        commands:
            ["echo hello world"]
            ["ls ."]

        結果は標準出力・標準エラー出力のタプルとして返される
        コマンドの出力が何もない場合、空の文字列が返される
        """

        out, err = "", ""
        try:
            out = self.__container.execute(command=command)
        except exceptions.DockerException as e:
            err = e.__str__()

        return out, err
