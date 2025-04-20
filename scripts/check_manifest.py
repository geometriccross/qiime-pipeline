#!/usr/bin/env python

import csv
import sys
import argparse
from typing import List
from textwrap import dedent
from pathlib import Path


def raise_error(message: str) -> None:
    """エラーメッセージを表示して終了する

    Args:
        message: エラーメッセージ
    """
    print(f"エラー: {message}", file=sys.stderr)
    sys.exit(1)


def validate_format(manifest_path: str) -> None:
    """マニフェストファイルのフォーマットを検証する

    Args:
        manifest_path: マニフェストファイルのパス
    """
    with open(manifest_path, "r") as f:
        # 列数の検証
        first_line = f.readline().strip()
        if first_line.count("\t") + 1 != 3:
            raise_error("マニフェストファイルの形式が不正です: 列数が3ではありません")
        f.seek(0)

        reader = csv.DictReader(f, delimiter="\t")
        required_fields = {
            "sample-id",
            "forward-absolute-filepath",
            "reverse-absolute-filepath",
        }

        # ヘッダーの検証
        if not all(field in reader.fieldnames for field in required_fields):
            missing = required_fields - set(reader.fieldnames or [])
            raise_error(f"必要なヘッダーが不足しています: {', '.join(missing)}")

        # データ行の列数を検証
        for row in reader:
            if len(row) != 3:
                raise_error(
                    "マニフェストファイルの形式が不正です: データ行の列数が3ではありません"
                )


def validate_manifest(manifest_path: str, **kwargs) -> None:
    """マニフェストファイルを検証する

    Args:
        manifest_path: マニフェストファイルのパス
        **kwargs: 追加のオプション引数
            - allow_missing: ファイルが存在しなくても許可する（デフォルト: False）

    以下の項目を検証:
    1. ファイルの形式（TSV形式、必要な列の存在）
    2. 参照されるファイルの存在（allow_missing=Falseの場合）
    3. forward/reverseファイル名の一貫性
    """
    if not Path(manifest_path).exists():
        raise_error(f"ファイルが存在しません: {manifest_path}")

    try:
        # フォーマットの検証を最初に行う
        validate_format(manifest_path)

        allow_missing = kwargs.get("allow_missing", False)
        errors = []

        # ファイルの存在とファイル名の一貫性をチェック
        with open(manifest_path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                sample_id = row["sample-id"]
                forward_path = row["forward-absolute-filepath"]
                reverse_path = row["reverse-absolute-filepath"]

                # ファイルの存在チェック（allow_missing=Falseの場合のみ）
                if not allow_missing:
                    if not Path(forward_path).exists():
                        errors.append(
                            f"forward-absolute-filepath が存在しません: "
                            f"{forward_path} (sample-id: {sample_id})"
                        )
                    if not Path(reverse_path).exists():
                        errors.append(
                            f"reverse-absolute-filepath が存在しません: "
                            f"{reverse_path} (sample-id: {sample_id})"
                        )

                # ファイル名の整合性チェック
                forward_name = Path(forward_path).name
                reverse_name = Path(reverse_path).name
                forward_sample = forward_name.split("_")[0]
                reverse_sample = reverse_name.split("_")[0]

                if forward_sample != reverse_sample:
                    errors.append(
                        f"id: {sample_id}, forward: ({forward_sample}) と "
                        f"reverse: ({reverse_sample}) が一致しません。"
                    )

            if errors:
                raise_error("\n".join(errors))

    except csv.Error as e:
        raise_error(f"マニフェストファイルの形式が不正です: {e}")


def main(argv: List[str] = None) -> None:
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
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="ファイルが存在しなくても許可する",
    )

    args = parser.parse_args(argv)
    validate_manifest(
        args.input_path,
        allow_missing=args.allow_missing,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
