from pathlib import Path
from typing import Union


class QiimeCommandBuilder:
    """QIIME2コマンドを構築するためのビルダークラス"""

    def __init__(self, base_command: str):
        """
        Args:
            base_command: 基本コマンド (e.g., "qiime tools import")
        """
        self.command_parts = [base_command]
        self.indent_level = 0

    def add_input(self, name: str, value: Union[str, Path]) -> "QiimeCommandBuilder":
        """
        Input パラメータの追加 (--i-*)

        Args:
            name: パラメータ名
            value: パラメータの値

        Returns:
            self: メソッドチェーン用
        """
        self.command_parts.append(f"    --i-{name} {value}")
        return self

    def add_output(self, name: str, value: Union[str, Path]) -> "QiimeCommandBuilder":
        """
        Output パラメータの追加 (--o-*)

        Args:
            name: パラメータ名
            value: パラメータの値

        Returns:
            self: メソッドチェーン用
        """
        self.command_parts.append(f"    --o-{name} {value}")
        return self

    def add_parameter(self, name: str, value: Union[str, int]) -> "QiimeCommandBuilder":
        """
        Parameter の追加 (--p-*)

        Args:
            name: パラメータ名
            value: パラメータの値

        Returns:
            self: メソッドチェーン用
        """
        self.command_parts.append(f"    --p-{name} {value}")
        return self

    def add_metadata(self, name: str, value: Union[str, Path]) -> "QiimeCommandBuilder":
        """
        Metadata の追加 (--m-*)

        Args:
            name: パラメータ名
            value: パラメータの値

        Returns:
            self: メソッドチェーン用
        """
        self.command_parts.append(f"    --m-{name} {value}")
        return self

    def add_option(self, name: str, value: str = "") -> "QiimeCommandBuilder":
        """
        オプションの追加 (--*)

        Args:
            name: オプション名
            value: オプションの値 (オプション)

        Returns:
            self: メソッドチェーン用
        """
        option = f"    --{name}"
        if value:
            option += f" {value}"
        self.command_parts.append(option)
        return self

    def build(self) -> list[str]:
        """
        コマンドのビルド

        Returns:
            list[str]: コマンドのリスト
        """
        return self.command_parts
