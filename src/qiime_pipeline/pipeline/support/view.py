#!/usr/bin/env python

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from zipfile import ZipFile
from typing import Optional


class ViewError(Exception):
    """ビュー処理に関連するエラーを表すカスタム例外クラス"""

    pass


class QzvViewer:
    """
    QZVファイル（QIIME 2 Visualization）をブラウザで表示するためのクラス
    このクラスはWSL環境での使用を想定している。
    """

    def __init__(self):
        """WSL環境とブラウザ設定を初期化"""
        self._validate_environment()
        self.browser = os.environ.get("BROWSER")
        self.temp_dir: Optional[Path] = None

    def _validate_environment(self) -> None:
        """WSL環境であることを確認

        Raises:
            ViewError: WSL環境でない、またはBROWSER環境変数が設定されていない場合
        """
        if not os.environ.get("WSL_DISTRO_NAME"):
            raise ViewError("このスクリプトはWSL環境で実行する必要があります")

        if not os.environ.get("BROWSER"):
            raise ViewError("BROWSER環境変数が設定されていません")

    def view(self, qzv_path: Path) -> None:
        """QZVファイルを展開してブラウザで表示

        QZVファイルはQIIME 2のVisualizationファイルで、
        ZIPアーカイブとしてdata/index.htmlを含んでいます。

        Args:
            qzv_path: 表示するQZVファイルのパス

        Raises:
            ViewError: ファイルが存在しない、または処理中にエラーが発生した場合
        """
        if not qzv_path.exists():
            raise ViewError(f"ファイル '{qzv_path}' が見つかりません")

        try:
            index_path = self._extract_index_html(qzv_path)
            win_path = self._convert_to_windows_path(index_path)
            self._open_in_browser(win_path)
        finally:
            if self.temp_dir and self.temp_dir.exists():
                self._cleanup()

    def _extract_index_html(self, qzv_path: Path) -> Path:
        """QZVファイルからdata/index.htmlを展開

        Args:
            qzv_path: 展開するQZVファイルのパス

        Returns:
            展開されたindex.htmlのパス

        Raises:
            ViewError: index.htmlが見つからない場合
        """
        self.temp_dir = Path(tempfile.mkdtemp())

        try:
            with ZipFile(qzv_path) as zip_file:
                zip_file.extractall(self.temp_dir)
                index_path = self.temp_dir / "data" / "index.html"
                if not index_path.exists():
                    raise ViewError("index.htmlが見つかりません")
                return index_path
        except Exception as e:
            raise ViewError(f"QZVファイルの展開に失敗しました: {str(e)}")

    def _convert_to_windows_path(self, path: Path) -> str:
        """LinuxパスをWindowsパスに変換

        wslpathコマンドを使用してパスを変換します。

        Args:
            path: 変換するLinuxパス

        Returns:
            変換されたWindowsパス

        Raises:
            ViewError: パス変換に失敗した場合
        """
        try:
            result = subprocess.run(
                ["wslpath", "-w", str(path)], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ViewError(f"パスの変換に失敗しました: {str(e)}")

    def _open_in_browser(self, path: str) -> None:
        """ブラウザでファイルを開く

        Args:
            path: 開くファイルのパス（Windowsパス形式）

        Raises:
            ViewError: ブラウザでの表示に失敗した場合
        """
        try:
            subprocess.run([self.browser, path], check=True)
        except subprocess.CalledProcessError as e:
            raise ViewError(f"ブラウザでの表示に失敗しました: {str(e)}")

    def _cleanup(self) -> None:
        """一時ディレクトリを削除"""
        import shutil

        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass  # cleanup失敗は無視


def _is_in_container() -> bool:
    """Dockerコンテナ内で実行されているかチェックする"""
    return os.path.exists("/.dockerenv")


if __name__ == "__main__":
    """メイン処理

    コマンドライン引数で指定されたQZVファイルを
    ブラウザで表示します。

    Note:
        このスクリプトはDocker環境外でのみ実行可能です。
        Docker環境内で実行するとエラーになります。
    """
    if _is_in_container():
        print("このスクリプトはDockerコンテナ内では実行できません", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) != 2:
        print("使用方法: view.py QZV_FILE_PATH", file=sys.stderr)
        sys.exit(1)

    try:
        viewer = QzvViewer()
        viewer.view(Path(sys.argv[1]))
    except ViewError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)
