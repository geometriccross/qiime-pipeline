from typing import Iterable
from .qiime_command import Q2Cmd
from .qiime_error import CircularDependencyError, IsolatedCommandError


class Q2CmdAssembly(Iterable[Q2Cmd]):
    """Q2CMDを保有し、依存関係を解決する"""

    def __init__(self):
        self.commands: list[Q2Cmd] = []
        self._index = 0

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
        temp = set()
        dependency_path = []

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
                raise CircularDependencyError(dependency_path, cmd)
            if cmd in visited:
                return

            # 依存関係のチェック
            if not has_any_dependency(cmd):
                raise IsolatedCommandError(cmd)

            temp.add(cmd)
            dependency_path.append(cmd)

            # このコマンドが依存するコマンドを先に処理
            for other in self.commands:
                if other < cmd:  # otherの出力がcmdの入力として使用される
                    visit(other)

            temp.remove(cmd)
            dependency_path.pop()
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
