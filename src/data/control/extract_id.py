import csv
import sys
import argparse
from textwrap import dedent
from typing import Iterator, List, Set


class ExtractError(Exception):
    """抽出処理に関連するエラーを表すカスタム例外クラス"""

    pass


def process_rows(
    file, targets: Set[str], column: int, exclude_mode: bool
) -> Iterator[List[str]]:
    """ファイルの各行を処理するジェネレータ関数

    Args:
        file: 入力ファイルオブジェクト
        targets: 抽出または除外対象のIDセット
        column: 対象とする列のインデックス
        exclude_mode: 除外モードフラグ

    Yields:
        処理対象の行データ
    """
    reader = csv.reader(file, delimiter="\t")

    try:
        header = next(reader)
        yield header
    except StopIteration:
        raise ExtractError("ファイルが空です")

    if column >= len(header):
        raise ExtractError(f"指定された列インデックス {column} が範囲外です")

    for row in reader:
        if len(row) <= column:
            continue

        match = row[column] in targets
        if (exclude_mode and not match) or (not exclude_mode and match):
            yield row


def extract_id(
    input_path: str, targets: List[str], column: int = 0, exclude_mode: bool = False
) -> Iterator[str]:
    """
    指定した列の値に基づいて、CSVデータの行を抽出または除外します。
    ジェネレータを使用してメモリ効率を改善しています。

    Args:
        input_path: 入力ファイルのパス
        targets: 抽出または除外するターゲットIDのリスト
        column: 対象とする列のインデックス（0始まり）
        exclude_mode: Trueの場合、ターゲットIDに一致する行を除外

    Yields:
        処理された各行のタブ区切り文字列

    Raises:
        ExtractError: ファイルが空、または列インデックスが無効な場合
        FileNotFoundError: 入力ファイルが存在しない場合
    """
    targets_set = set(targets)  # 検索効率向上のためsetに変換

    try:
        with open(input_path, newline="") as file:
            for row in process_rows(file, targets_set, column, exclude_mode):
                yield "\t".join(row)
    except FileNotFoundError:
        raise ExtractError(f"ファイル '{input_path}' が見つかりません")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="指定した列の値に基づいて、CSVデータの行を抽出または除外します。"
    )
    parser.add_argument(
        "input_path",
        help=dedent(
            """
            データ、メタデータ、またはマニフェストのファイルパス
            """
        ),
    )
    parser.add_argument(
        "targets",
        nargs="+",
        help=dedent(
            """
            抽出対象のID（複数指定可）
            """
        ),
    )
    parser.add_argument(
        "-c",
        "--column",
        type=int,
        default=0,
        help=dedent(
            """
            対象とする列のインデックス（0始まり）
            """
        ),
    )
    parser.add_argument(
        "-r",
        "--exclude",
        action="store_true",
        help=dedent(
            """
            このオプションが指定された場合、ターゲットIDに一致する行を除外します。
            （指定がない場合は、一致する行のみを出力します）
            """
        ),
    )

    args = parser.parse_args()

    try:
        for line in extract_id(
            args.input_path, args.targets, args.column, args.exclude
        ):
            print(line)
    except ExtractError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
