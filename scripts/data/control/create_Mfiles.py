#!/usr/bin/env python

import re
import csv
import argparse
from textwrap import dedent
from pathlib import Path, PurePath
from scripts.data.store.dataset import Datasets
from scripts.data.store.used_data import used_data


# queryで渡されたidを持つfastqファイルを返す
def search_fastq(q: str, data: list[str]) -> tuple[str]:
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

    fwd_abs_path = Path(fwd).absolute().__str__()
    rvs_abs_path = Path(rvs).absolute().__str__()
    return fwd_abs_path, rvs_abs_path


def get_header(meta_path: str) -> list[str]:
    """
    指定されたメタデータファイルのヘッダーを取得する
    """
    assert Path(meta_path).exists(), f"{meta_path} does not exist"
    with Path(meta_path).open() as f:
        header_str = f.readline().replace("\n", "")
        return header_str.replace("#", "").replace("SampleID", "RawID").split(",")


def header_replaced(header_arr: list[str], id_prefix) -> list[list[str]]:
    # csv writerowsで正常に書き込むためには二次元配列でなければならない
    return [
        [
            id_prefix,
            header_arr[0].replace("SampleID", "RawID").replace("#", ""),
            *header_arr[1:],
        ]
    ]


def create_Mfiles(
    id_prefix: str,
    out_meta: str,
    out_mani: str,
    data: Datasets,
) -> None:
    """
    Create metadata and manifest files from the given data.
    """
    mani_result = [
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"]
    ]

    # 全データを一時リストに収集（ヘッダーなし）
    rows_with_files = []
    for dataset in data.sets:
        with open(Path(dataset.metadata_path).absolute(), "r") as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダーをスキップ
            # データセットの各行を保存（RawIDとfastqファイルのペア）
            for row in reader:
                rows_with_files.append((row, dataset.fastq_files))

    # RawIDでソート（test1, test2, ...の順）
    rows_with_files.sort(key=lambda x: x[0][0])  # row[0][0]がRawID

    # メタデータファイルを作成
    # 最初のデータセットからヘッダーを取得
    retrived_path = next(iter(data.sets)).metadata_path
    header = header_replaced(get_header(retrived_path), id_prefix)
    master_list = [header[0]]  # ヘッダー行のみを追加

    # ソート済みデータにIDを付与
    for i, (row, fastq_files) in enumerate(rows_with_files, start=1):
        # master csv
        master_list.append([id_prefix + str(i), *row])

        # manifest
        # RawIDから対応するfastqファイルを取得
        mani_result.append(
            [
                id_prefix + str(i),
                *search_fastq(row[0], fastq_files),
            ]
        )

    # ヘッダーを含むmaniフォーマット
    mani_result = [
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"],
        *mani_result[1:],
    ]

    with open(out_meta, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(master_list)

    with open(out_mani, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(mani_result)


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
