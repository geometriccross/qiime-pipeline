#!/usr/bin/env python

import csv
import argparse
from textwrap import dedent
from pathlib import Path
from typing import Dict, List


class ManifestError(Exception):
    """マニフェストファイルの検証に関するエラーを表すカスタム例外クラス"""

    pass


class ManifestChecker:
    """マニフェストファイルの検証を行うクラス"""

    def __init__(self, manifest_path: str):
        """
        Args:
            manifest_path (str): 検証するマニフェストファイルのパス
        """
        self.manifest_path = Path(manifest_path)
        self.errors: List[str] = []

    def validate(self) -> None:
        """
        マニフェストファイルの検証を実行する

        Raises:
            ManifestError: マニフェストファイルに不整合がある場合
            FileNotFoundError: マニフェストファイルが存在しない場合
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"マニフェストファイルが見つかりません: {self.manifest_path}"
            )

        try:
            with open(self.manifest_path, "r") as f:
                content = f.readlines()

                # フォーマットチェック
                expected_columns = 3
                for i, line in enumerate(content):
                    if line.count("\t") + 1 != expected_columns:
                        raise ManifestError(
                            f"マニフェストファイルの形式が不正です: {i+1}行目の列数が{expected_columns}ではありません"
                        )

                # DictReaderでの検証
                reader = csv.DictReader(content, delimiter="\t")
                self._validate_rows(reader)

                if self.errors:
                    raise ManifestError("\n".join(self.errors))
        except (csv.Error, StopIteration) as e:
            raise ManifestError(f"マニフェストファイルの形式が不正です: {e}")

    def _validate_rows(self, reader: csv.DictReader) -> None:
        """
        マニフェストファイルの各行を検証する

        Args:
            reader (csv.DictReader): マニフェストファイルのリーダー
        """
        required_fields = {
            "sample-id",
            "forward-absolute-filepath",
            "reverse-absolute-filepath",
        }

        # ヘッダーの検証
        if not all(field in reader.fieldnames for field in required_fields):
            missing = required_fields - set(reader.fieldnames or [])
            self.errors.append(f"必要なヘッダーが不足しています: {', '.join(missing)}")
            return

        for row in reader:
            self._validate_row(row)

    def _validate_row(self, row: Dict[str, str]) -> None:
        """
        マニフェストファイルの1行を検証する

        Args:
            row (Dict[str, str]): 検証する行のデータ
        """
        sample_id = row["sample-id"]
        forward_path = row["forward-absolute-filepath"]
        reverse_path = row["reverse-absolute-filepath"]

        # パスの存在チェック
        if not Path(forward_path).exists():
            self.errors.append(
                f"forward-absolute-filepath が存在しません: "
                f"{forward_path} (sample-id: {sample_id})"
            )
        if not Path(reverse_path).exists():
            self.errors.append(
                f"reverse-absolute-filepath が存在しません: "
                f"{reverse_path} (sample-id: {sample_id})"
            )

        # ファイル名の整合性チェック
        forward_name = Path(forward_path).name
        reverse_name = Path(reverse_path).name
        forward_sample = forward_name.split("_")[0]
        reverse_sample = reverse_name.split("_")[0]

        if forward_sample != reverse_sample:
            self.errors.append(
                f"id: {sample_id}, forward: ({forward_sample}) と "
                f"reverse: ({reverse_sample}) が一致しません。"
            )


def main() -> None:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="マニフェストファイルの検証を行うスクリプト"
    )
    parser.add_argument(
        "input_path",
        help=dedent(
            """
            検証するマニフェストファイルのパス
            タブ区切りのCSVファイルで、以下のヘッダーが必要:
            - sample-id
            - forward-absolute-filepath
            - reverse-absolute-filepath
        """
        ),
    )

    args = parser.parse_args()
    checker = ManifestChecker(args.input_path)

    try:
        checker.validate()
    except (ManifestError, FileNotFoundError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import sys

    main()
