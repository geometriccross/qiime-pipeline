from pathlib import Path
from typing import Iterable, List
from python_on_whales import docker, exceptions
from python_on_whales import Container, Image


class Provider:
    def __init__(
        self,
        image: str | Image,
        mounts: Iterable[List[str]] = (),
        workspace: Path = Path("."),
        remove=True,
    ):
        if isinstance(image, str):
            self.__image = docker.image.pull(image)
        else:
            self.__image = image

        self.__mounts = mounts
        self.__workspace = workspace
        self.__remove = remove

        self.__container: Container = None

    def provide(self) -> Container:
        self.__container = docker.container.run(
            image=self.__image,
            mounts=self.__mounts,
            workdir=self.__workspace.absolute(),
            command=["tail", "-f", "/dev/null"],
            detach=True,
            remove=self.__remove,
        )

        return self.__container

    @classmethod
    def from_dockerfile(
        cls,
        dockerfile: Path,
        mounts: Iterable[List[str]] = (),
        workspace: Path = Path("."),
        remove=True,
    ):
        image = docker.image.build(context_path=dockerfile.parent, file=dockerfile)
        return cls(image=image, mounts=mounts, workspace=workspace, remove=remove)

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
        status = getattr(ctn.state, "status", None)

        # 処理能力の高低により、removing状態が取得される場合があるため
        # 一括してabsentとしてみなす
        if status == "removing":
            return "absent"
        return status


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

    def run(self, command: list[str]) -> tuple[str, str]:
        """コンテナ内でコマンドを実行する

        Args:
            command (list[str])
                以下の形式でコマンドを指定する
                ["echo", "Hello World!"]

        Returns:
            tuple[str, str]: 実行結果の標準出力と標準エラー出力
        """

        return CommandRunner(self.__container).run(command=command)


class CommandRunner:
    def __init__(self, container: Container):
        self.__container = container

    @classmethod
    def __wrap_cmd(cls, command: str) -> str:
        """
        docker execではentorypointを経由せず直接コマンドを実行するためbase環境が認識されない。
        それを回避するため、micromambaを使用してbase環境を明示的に指定する。

        これは渡されたcommandに必要な引数を付加して返す関数である。
        """
        pre_cmd = "micromamba run -n base bash -exc "
        return pre_cmd + command

    def run(self, command: list[str]) -> str:
        """
        文字列としてcommandを受け取り、実行する
        成功すれば標準出力を返し、失敗すれば例外を投げる
        """

        out, err = "", ""
        try:
            out = self.__container.execute(command)
        except exceptions.DockerException as e:
            err = e.__str__()

        if err:
            err = f"Command failed with error:\n {err}"
            raise RuntimeError(err)

        return out

    def try_run(self, command: list[str]) -> tuple[str, str]:
        """
        文字列としてcommandを受け取り、実行する

        結果は標準出力・標準エラー出力のタプルとして返される
        コマンドの出力が何もない場合、空の文字列が返される
        """

        out, err = "", ""
        try:
            out = self.run(command)
        except Exception as e:
            err = e.__str__()

        return out, err
