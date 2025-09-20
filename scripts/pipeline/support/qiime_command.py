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

    def __hash__(self):
        return hash((tuple(self.command_parts), tuple(self.__base_cmd)))

    def __eq__(self, other: Q2Cmd) -> bool:
        """
        == 演算子のオーバーライド
        依存関係がない場合にTrue
        """
        if not isinstance(other, Q2Cmd):
            return NotImplemented

        no_dependency = not (self < other or self > other)
        same_hash = hash(self) == hash(other)
        return no_dependency and same_hash

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

    def sort_commands(self) -> None:
        """
        コマンドを依存関係に基づいてソートする
        依存関係はQ2Cmdの__lt__と__gt__メソッドで判定される
        どのコマンドとも依存関係を持たない孤立したコマンドが検出された場合、
        ValueError例外を投げる
        """
        sorted_commands = []
        visited = set()
        temp = set()

        def has_any_dependency(cmd: Q2Cmd) -> bool:
            """
            コマンドが他のコマンドと依存関係を持っているかをチェックする

            Args:
                cmd (Q2Cmd): チェック対象のコマンド

            Returns:
                bool: 依存関係が存在する場合True、存在しない場合False
            """
            for other in self.commands:
                if cmd != other and (cmd < other or cmd > other):
                    return True
            return False

        def visit(cmd: Q2Cmd) -> None:
            if cmd in temp:
                raise ValueError("循環依存関係が検出されました")
            if cmd in visited:
                return

            # 依存関係のチェック
            if not has_any_dependency(cmd):
                raise ValueError(f"孤立したコマンドが検出されました: {str(cmd)}")

            temp.add(cmd)
            # このコマンドが依存するコマンドを先に処理
            for other in self.commands:
                if other < cmd:  # otherの出力がcmdの入力として使用される
                    visit(other)
            temp.remove(cmd)
            visited.add(cmd)
            sorted_commands.append(cmd)

        # 全てのコマンドに対してDFSを実行
        for cmd in self.commands:
            if cmd not in visited:
                visit(cmd)

        # ソート済みのリストで更新
        self.commands = sorted_commands

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

    def build_all(self) -> list[list[str]]:
        """
        全てのコマンドをビルドする

        Returns:
            list[list[str]]: 各コマンドのリスト
        """
        return [cmd.build() for cmd in self.commands]
