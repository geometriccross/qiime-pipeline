from __future__ import annotations
from pathlib import Path
from typing import Union


class Q2CmdAssembly:
    """QIIME2コマンドを構築するためのビルダークラス"""

    def __init__(self, base_command: str):
        """
        実行するコマンドを指定する
        """
        self.command_parts = base_command.split(" ")

    def add_input(self, name: str, value: Union[str, Path]) -> Q2CmdAssembly:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--i-{name} {value}**
        """

        self.command_parts.extend([f"--i-{name}", f"{value}"])
        return self

    def add_output(self, name: str, value: Union[str, Path]) -> Q2CmdAssembly:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--o-{name} {value}**
        """

        self.command_parts.extend([f"--o-{name}", f"{value}"])
        return self

    def add_parameter(self, name: str, value: Union[str, int]) -> Q2CmdAssembly:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--p-{name} {value}**
        """

        self.command_parts.extend([f"--p-{name}", f"{value}"])
        return self

    def add_metadata(self, name: str, value: Union[str, Path]) -> Q2CmdAssembly:
        """
        渡されたnameとvalueを以下の形式でコマンドに追加する。\n
        **--m-{name} {value}**
        """

        self.command_parts.extend([f"--m-{name}", f"{value}"])
        return self

    def add_option(self, name: str, value: str = "") -> Q2CmdAssembly:
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
        return self.command_parts
