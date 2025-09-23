from __future__ import annotations
from typing import Iterable
from .qiime_command import Q2Cmd
from .qiime_error import CircularDependencyError, IsolatedCommandError


class Q2CmdAssembly(Iterable[Q2Cmd]):
    """Q2CMDを保有し、依存関係を解決する"""

    def __init__(self):
        self.commands: list[Q2Cmd] = []

    def __add__(self, other: Q2CmdAssembly) -> Q2CmdAssembly:
        new_assembly = Q2CmdAssembly()
        new_assembly.commands = self.commands + other.commands
        new_assembly.sort_commands()
        return new_assembly

    def sort_commands(self) -> None:
        """
        コマンドを依存関係に基づいてソートする
        依存関係はQ2Cmdの__lt__と__gt__メソッドで判定される

        Raises:
            CircularDependencyError: 循環依存関係が検出された場合
            IsolatedCommandError: どのコマンドとも依存関係を持たない孤立したコマンドが検出された場合
        """
        sorted_commands = []
        visited = set()

        # 一時的に訪問中のノードを保持するセット
        # 実行上の性能面から、stack_traceとは別にsetとして使用する
        cycle_detection_set = set()
        stack_trace = []

        def has_any_dependency(cmd: Q2Cmd) -> bool:
            """
            コマンドが他のコマンドと依存関係を持っているかをチェックする

            Args:
                cmd (Q2Cmd): チェック対象のコマンド

            Returns:
                bool: 依存関係が存在する場合True、存在しない場合False
            """

            for other in self.commands:
                not_self = cmd != other
                has_dependency = cmd < other or cmd > other

                if not_self and has_dependency:
                    return True

            return False

        def visit(cmd: Q2Cmd) -> None:
            if cmd in cycle_detection_set:
                raise CircularDependencyError(stack_trace, cmd)
            if cmd in visited:
                return

            # 依存関係のチェック
            if not has_any_dependency(cmd):
                raise IsolatedCommandError(cmd)

            cycle_detection_set.add(cmd)
            stack_trace.append(cmd)

            # otherの出力がcmdの入力として使用される全てのコマンドに対してDFSを実行
            for other in filter(lambda other: other < cmd, self.commands):
                visit(other)

            cycle_detection_set.remove(cmd)
            stack_trace.pop()

            visited.add(cmd)
            sorted_commands.append(cmd)

        for other in self.commands:
            if other not in visited:
                visit(other)

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
