#!/usr/bin/env python

import re
import csv
import argparse
from textwrap import dedent
from pathlib import Path, PurePath
from scripts.data.store.dataset import Datasets
from scripts.data.store.used_data import used_data
from .validate_pattern import Direction, check_current_pair, extract_first_underscore


class Pair:
    def __init__(self, forward: str, reverse: str) -> None:
        if not check_current_pair(forward, reverse):
            raise ValueError(f"Invalid pair: {forward}, {reverse}")

        self.name: str = PurePath(forward).stem
        self.forward: Direction.Forward = forward
        self.reverse: Direction.Reverse = reverse


def search_fastq_pair(q: str, data: list[str]) -> Pair:
    correct = []
    for d in data:
        file_name = PurePath(d).name
        if re.match(f"^{q.upper()}_", file_name.upper()):
            correct.append(d)

    # R1, R2以外に名前がかぶっているfastqファイルがあったら
    if len(correct) > 2:
        raise SyntaxError(
            dedent(
                f"""
            同名のファイルが3つ以上存在しています。\n
            {correct}
        """
            )
        )

    fwd = list(filter(lambda s: "_R1" in str(s), correct)).pop()
    rvs = list(filter(lambda s: "_R2" in str(s), correct)).pop()

    return Pair(fwd, rvs)


def pairwised_files(files: list[Path]) -> dict[Pair]:
    # 破壊的な変更が起きないようコピー
    bulk: list[Path] = files.copy()

    result = dict()
    while len(bulk) > 1:
        prob_fwd = str(bulk.pop())
        prob_rvs = str(bulk.pop())

        if check_current_pair(prob_fwd, prob_rvs):
            key = extract_first_underscore(PurePath(prob_fwd).name)
            result[key] = Pair(prob_fwd, prob_rvs)
        else:
            bulk.append(prob_fwd)
            bulk.append(prob_rvs)

    return result


def get_header(meta_path: str) -> list[str]:
    """
    指定されたメタデータファイルのヘッダーを取得する
    """
    assert Path(meta_path).exists(), f"{meta_path} does not exist"
    with Path(meta_path).open() as f:
        header_str = f.readline().replace("\n", "")
        return header_str.replace("#", "").replace("SampleID", "RawID").split(",")


def combine_all_metadata(datasets: Datasets) -> list[list[str]]:
    """
    Datasetsに含まれる全てのDatasetのメタデータを一つのリストにまとめて返す
    """

    all_metadata = []
    for dataset in datasets.sets:
        header_removed = dataset.metadata[1:]
        all_metadata.extend(header_removed)

    all_metadata.sort(key=lambda x: x[0])  # RawIDでソート（test1, test2, ...の順）
    return [get_header(list(datasets.sets)[0].metadata_path), *all_metadata]


def linked_table_expose(
    metadata: list[list[str]], pairwised: dict[Pair], id_prefix: str = "id"
) -> tuple[list, list]:
    manifest_table = [
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"]
    ]
    for i, key in enumerate([row[0] for row in metadata[1:]], start=1):
        id_name = id_prefix + str(i)
        manifest_table.append([id_name, pairwised[key].forward, pairwised[key].reverse])

    metadata_table = [["#SampleID", *metadata[0]]]
    for i, row in enumerate(metadata[1:], start=1):
        id_name = id_prefix + str(i)
        metadata_table.append([id_name, *row[1:]])

    return metadata_table, manifest_table


def add_id(
    rows_with_files: tuple[list[str], list[str]], id_prefix: str = "id", start: int = 1
) -> list[tuple[list[str], list[str]]]:
    """
    Listの各行にIDを追加して返す

    Args:
        rows_with_files (tuple[list[str], list[str]]): 各行のデータと対応するfastqファイルのリスト
        id_prefix (str, optional): 追加するIDのプレフィックス. Defaults to "id".
        start (int, optional): IDの開始番号. Defaults to 1.

    Returns:
        以下のように、それぞれの要素の先頭にidが付加されたリストを返す\n
        [[id1, hoge, huga], [id1, forward-absolute-filepath, ...]]

    """

    meta = []
    mani = []
    for i, (row, fastq_files) in enumerate(rows_with_files, start=1):
        # master csv
        meta.append([id_prefix + str(i), *row])

        # manifest
        # RawIDから対応するfastqファイルを取得
        mani.append(
            [
                id_prefix + str(i),
                *search_fastq(row[0], fastq_files),
            ]
        )

    return meta, mani


def create_Mfiles(
    id_prefix: str,
    out_meta: str,
    out_mani: str,
    data: Datasets,
) -> None:
    """
    Create metadata and manifest files from the given data.
    """

    rows_with_files = combine_all_metadata(data)

    # メタデータファイルを作成
    # 最初のデータセットからヘッダーを取得
    retrived_path = next(iter(data.sets)).metadata_path
    header = header_replaced(get_header(retrived_path), id_prefix)

    meta = [header[0]]  # ヘッダー行のみを追加
    mani = [
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"],
    ]

    added_meta, added_mani = add_id(rows_with_files, id_prefix, 1)
    meta.extend(added_meta)
    mani.extend(added_mani)

    with open(out_meta, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(meta)

    with open(out_mani, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(mani)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--id-prefix",
        default="id",
        help=dedent(
            """
            set prefix id of each sample like this [REPLACE THIS] + numeric
            (default : %(default)s))
            """
        ).strip(),
    )
    parser.add_argument("--input-meta", default="/meta")
    parser.add_argument("--input-fastq", default="/fastq")
    parser.add_argument(
        "--out-meta",
        help=dedent(
            """
            output path to metadata
            """
        ).strip(),
    )
    parser.add_argument(
        "--out-mani",
        help=dedent(
            """
            output path to manifest file
            """
        ).strip(),
    )
    parser.add_argument(
        "--meta-fastq-pair",
        help=dedent(
            """
            set a DICTIONARY metadata and fastq file pathes as a pair.
            e.g. --meta-fastq-pair {meta: /foo/bar/metafile.csv,/hoge/huga/fastqdir}
            """
        ).strip(),
    )

    # 引数から取得
    args = parser.parse_args()
    id_prefix = args.id_prefix
    input_meta = args.input_meta
    input_fastq = args.input_fastq
    out_meta = args.out_meta
    out_mani = args.out_mani
    # 引数のdefaultで指定してないのは、その段階ではまだ割り当てられていないinput_metaを使いたかったから

    create_Mfiles(id_prefix, out_meta, out_mani, used_data())
