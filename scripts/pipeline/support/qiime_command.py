from __future__ import annotations
from pathlib import Path
from typing import Union, Iterable


class Q2Cmd:
    def __init__(self, base_command: str):
        """
        実行するコマンドを指定する
        """
        self.__base_cmd = base_command.split(" ")
        self.command_parts = []

    def __str__(self):
        return " ".join(self.__base_cmd)

    def _get_paths_from_parts(self, prefix: str) -> list[str]:
        """
        command_partsから特定のプレフィックスを持つパスを取得する

        Args:
            prefix: '--i-' または '--o-'

        Returns:
            list[str]: 見つかったパスのリスト
        """
        paths = []
        for i, part in enumerate(self.command_parts):
            if part.startswith(prefix) and i + 1 < len(self.command_parts):
                paths.append(self.command_parts[i + 1])

        return paths

    def __lt__(self, other: Q2Cmd) -> bool:
        """
        < 演算子のオーバーライド
        selfの出力がotherの入力として使用される場合にTrue
        """
        my_outputs = set(self._get_paths_from_parts("--o-"))
        other_inputs = set(other._get_paths_from_parts("--i-"))
        for my_output in my_outputs:
            if my_output in other_inputs:
                return True  # 中断する

        return False

    def __gt__(self, other: Q2Cmd) -> bool:
        """
        > 演算子のオーバーライド
        otherの出力がselfの入力として使用される場合にTrue
        """
        return other < self

    def __eq__(self, other: Q2Cmd) -> bool:
        """
        == 演算子のオーバーライド
        依存関係がない場合にTrue
        """
        if not isinstance(other, Q2Cmd):
            return NotImplemented

        no_dependency = not (self < other or self > other)
        same_value = (
            self.command_parts == other.command_parts
            and self.__base_cmd == other.__base_cmd
        )
        return no_dependency and same_value

    def add_input(self, name: str, value: Union[str, Path]) -> Q2Cmd:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--i-{name} {value}**
        """

        self.command_parts.extend([f"--i-{name}", f"{value}"])
        return self

    def add_output(self, name: str, value: Union[str, Path]) -> Q2Cmd:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--o-{name} {value}**
        """

        self.command_parts.extend([f"--o-{name}", f"{value}"])
        return self

    def add_parameter(self, name: str, value: Union[str, int]) -> Q2Cmd:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--p-{name} {value}**
        """

        self.command_parts.extend([f"--p-{name}", f"{value}"])
        return self

    def add_metadata(self, name: str, value: Union[str, Path]) -> Q2Cmd:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--m-{name} {value}**
        """

        self.command_parts.extend([f"--m-{name}", f"{value}"])
        return self

    def add_option(self, name: str, value: str = "") -> Q2Cmd:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--{name} {value}**
        """

        option = [f"--{name}"]
        if value:
            option.append(f"{value}")
        self.command_parts.extend(option)
        return self

    def build(self) -> list[str]:
        """
        コマンドのビルド

        Returns:
            list[str]: コマンドのリスト
        """
        return self.__base_cmd + self.command_parts


class Q2CmdAssembly(Iterable[Q2Cmd]):
    """Q2CMDを保有し、依存関係を解決する"""

    def __init__(self):
        self.commands: list[Q2Cmd] = []
        self._index = 0

    def __iter__(self) -> Iterable[Q2Cmd]:
        return iter(self.commands)

    def new_cmd(self, base_command: str) -> Q2Cmd:
        """
        新しいQ2Cmdインスタンスを作成し、アセンブリに追加する

        Args:
            base_command (str): コマンドの基本部分

        Returns:
            Q2Cmd: 作成されたQ2Cmdインスタンス
        """
        cmd = Q2Cmd(base_command)
        self.commands.append(cmd)
        return cmd
