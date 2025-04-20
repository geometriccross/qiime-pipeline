#!/usr/bin/env python

import re
import csv
import argparse
from glob import glob
from pathlib import Path
from typing import List, Tuple
from .config import (
    DataSource,
    DATA_LIST,
    DEFAULT_ID_PREFIX,
    DEFAULT_META_DIR,
    DEFAULT_FASTQ_DIR,
)


class FastqFileNotFoundError(Exception):
    """FASTQファイルが見つからない場合のエラー"""

    pass


class DuplicateFastqError(Exception):
    """同名のFASTQファイルが3つ以上存在する場合のエラー"""

    pass


class FastqProcessor:
    """FASTQファイルの処理を行うクラス"""

    @staticmethod
    def search_fastq(query: str, data: List[str]) -> Tuple[str, str]:
        """
        queryで指定されたIDを持つFASTQファイルのペアを返す

        Args:
            query: 検索するID
            data: 検索対象のファイルパスリスト

        Returns:
            Tuple[str, str]: Forward, Reverseのファイルパスのタプル

        Raises:
            FastqFileNotFoundError: FASTQファイルが見つからない場合
            DuplicateFastqError: 同名のファイルが3つ以上存在する場合
        """
        correct = []
        for d in data:
            file_name = Path(d).name
            if re.match(f"^{query.upper()}_", file_name.upper()):
                correct.append(d)

        if not correct:
            raise FastqFileNotFoundError(f"FASTQファイルが見つかりません: {query}")

        if len(correct) > 2:
            raise DuplicateFastqError(
                f"同名のファイルが3つ以上存在しています: {correct}"
            )

        try:
            fwd = next(s for s in correct if "_R1_" in s)
            rvs = next(s for s in correct if "_R2_" in s)
        except StopIteration:
            raise FastqFileNotFoundError(
                f"R1またはR2のFASTQファイルが見つかりません: {query}"
            )

        return str(Path(fwd).absolute()), str(Path(rvs).absolute())


class MetadataProcessor:
    """メタデータの処理を行うクラス"""

    def __init__(self, id_prefix: str):
        self.id_prefix = id_prefix
        self.master_list: List[List[str]] = []
        self.manifest_list: List[List[str]] = []

    def initialize_master_list(self, first_meta_path: str) -> None:
        """マスターリストのヘッダーを初期化"""
        with Path(first_meta_path).open() as f:
            header = f.readline().strip()
            self.master_list = [
                [
                    self.id_prefix,
                    *header.replace("#", "").replace("SampleID", "RawID").split(","),
                ]
            ]

    def initialize_manifest_list(self) -> None:
        """マニフェストリストのヘッダーを初期化"""
        self.manifest_list = [
            ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"]
        ]

    def process_metadata(self, data_sources: List[DataSource]) -> None:
        """全てのメタデータを処理"""
        id_index = 1
        fastq_processor = FastqProcessor()

        for source in data_sources:
            meta_path = source["meta"]
            fastq_dir = source["fastq"]
            fastq_paths = glob(f"{fastq_dir}/**/*gz", recursive=True)

            with Path(meta_path).open() as f:
                reader = csv.reader(f)
                next(reader)  # ヘッダーをスキップ
                for row in reader:
                    current_id = f"{self.id_prefix}{id_index}"

                    # マスターリストに追加
                    self.master_list.append([current_id, *row])
                    # マニフェストに追加
                    try:
                        fwd, rvs = fastq_processor.search_fastq(row[0], fastq_paths)
                        self.manifest_list.append([current_id, fwd, rvs])
                    except (FastqFileNotFoundError, DuplicateFastqError) as e:
                        print(
                            f"警告: サンプル {row[0]} の処理中にエラーが発生しました: {e}"
                        )
                        continue

                    id_index += 1


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="メタデータとマニフェストファイルを生成"
    )
    parser.add_argument(
        "-p",
        "--id-prefix",
        default=DEFAULT_ID_PREFIX,
        help=f"サンプルIDのプレフィックス (default: {DEFAULT_ID_PREFIX})",
    )
    parser.add_argument(
        "--input-meta",
        default=DEFAULT_META_DIR,
        help=f"メタデータの入力ディレクトリ (default: {DEFAULT_META_DIR})",
    )
    parser.add_argument(
        "--input-fastq",
        default=DEFAULT_FASTQ_DIR,
        help=f"FASTQファイルの入力ディレクトリ (default: {DEFAULT_FASTQ_DIR})",
    )
    parser.add_argument(
        "--out-meta", required=True, help="出力するメタデータファイルのパス"
    )
    parser.add_argument(
        "--out-mani", required=True, help="出力するマニフェストファイルのパス"
    )
    return parser.parse_args()


def main() -> None:
    """メイン処理"""
    args = parse_args()

    # データソースのパスを更新
    data_sources = [
        {
            "meta": f"{args.input_meta}/{Path(d['meta']).name}",
            "fastq": f"{args.input_fastq}/{Path(d['fastq']).name}",
        }
        for d in DATA_LIST
    ]

    try:
        processor = MetadataProcessor(args.id_prefix)
        processor.initialize_master_list(data_sources[0]["meta"])
        processor.initialize_manifest_list()
        processor.process_metadata(data_sources)

        # 結果を保存
        with open(args.out_meta, "w") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(processor.master_list)

        with open(args.out_mani, "w") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(processor.manifest_list)

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
