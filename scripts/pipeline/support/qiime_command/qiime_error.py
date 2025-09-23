from .qiime_command import Q2Cmd


class QiimePipelineError(Exception):
    """QIIMEパイプラインの基底エラークラス"""

    pass


class DependencyError(QiimePipelineError):
    """依存関係に関するエラーの基底クラス"""

    def __init__(self, message: str, commands: list[Q2Cmd]):
        self.commands = commands
        super().__init__(message)


class CircularDependencyError(DependencyError):
    """循環依存関係を検出した際のエラー"""

    def __init__(self, stack_trace: list[Q2Cmd], current_cmd: Q2Cmd):
        cycle_path = self._build_cycle_path(stack_trace, current_cmd)
        message = self._format_error_message(cycle_path)
        super().__init__(message, cycle_path)

    @staticmethod
    def _build_cycle_path(stack_trace: list[Q2Cmd], current_cmd: Q2Cmd) -> list[Q2Cmd]:
        """
        循環依存関係の完全なパスを構築する。
        依存関係の順序に従ってコマンドを並べ替え、サイクルを完成させる。

        Args:
            stack_trace: これまでの依存関係のパス
            current_cmd: サイクルの開始点となるコマンド

        Returns:
            list[Q2Cmd]: 依存関係の順序に従って並べられたコマンドのリスト
        """
        # サイクルの開始位置を特定し、そこからのパスを抽出
        cycle_start_index = stack_trace.index(current_cmd)
        cycle = stack_trace[cycle_start_index:]

        # サイクルを完成させるため、最後に開始点を追加
        cycle.append(current_cmd)

        # 依存関係に基づいて並べ替え
        for i in range(len(cycle) - 1):
            current = cycle[i]
            next_cmd = cycle[i + 1]

            if current.has_dependency(next_cmd):
                continue

            # 隣接するコマンド間に依存関係がない場合、さらに次のcmdを参照する
            for j in range(i + 1, len(cycle)):
                if current.has_dependency(cycle[j]):
                    cycle[i + 1], cycle[j] = cycle[j], cycle[i + 1]
                    break

        return cycle

    def _format_error_message(self, cycle_path: list[Q2Cmd]) -> str:
        """循環依存関係のエラーメッセージを生成"""
        cycle_details = []
        for i in range(len(cycle_path) - 1):
            current = cycle_path[i]
            next_cmd = cycle_path[i + 1]
            direction = "->" if current < next_cmd else "<-"
            cycle_details.append(f"{current} {direction} {next_cmd}")

        return (
            "循環依存関係が検出されました:\n"
            "依存関係のパス:\n"
            f"{chr(10).join(cycle_details)}"
        )


class IsolatedCommandError(DependencyError):
    """孤立したコマンドを検出した際のエラー"""

    def __init__(self, command: Q2Cmd):
        message = f"孤立したコマンドが検出されました: {str(command)}"
        super().__init__(message, [command])
