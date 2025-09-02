#!/usr/bin/env python

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


def pairwise(datasets: Datasets) -> dict[Pair]:
    """
    pairwised_filesを呼び出す関数
    datasetsを適切な形に変換してpairwised_filesに渡す
    """

    all_fastq = []
    for dataset in datasets.sets:
        all_fastq.extend(dataset.fastq_files)

    return pairwised_files(all_fastq)


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


def create_Mfiles(
    out_meta: str,
    out_mani: str,
    data: Datasets,
    id_prefix: str = "id",
) -> None:
    """
    Create metadata and manifest files from the given data.
    """

    metadata = combine_all_metadata(data)
    pairwised = pairwise(data)
    metatable, manifest = linked_table_expose(metadata, pairwised, id_prefix)

    with open(out_meta, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(metatable)

    with open(out_mani, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(manifest)


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
