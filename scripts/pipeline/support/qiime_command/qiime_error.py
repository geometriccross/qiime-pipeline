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
        循環依存関係の完全なパスを構築する

        Args:
            stack_trace: これまでの依存関係のパス
            current_cmd: サイクルの開始点となるコマンド

        Returns:
            list[Q2Cmd]: 依存関係の順序に従って並べられたコマンドのリスト
        """
        cmd_pos = stack_trace.index(current_cmd)
        cycle = stack_trace[cmd_pos:]
        cycle.append(current_cmd)  # サイクルを完成させるため、最後に開始点を追加

        # 依存関係の順序を確認
        for i in range(len(cycle) - 1):
            current = cycle[i]
            next_cmd = cycle[i + 1]

            if not (current < next_cmd or next_cmd < current):
                # 依存関係がない場合は順序を入れ替える
                for j in range(i + 2, len(cycle)):
                    if current < cycle[j] or cycle[j] < current:
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
