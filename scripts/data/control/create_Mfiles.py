#!/usr/bin/env python

import csv
from pathlib import Path, PurePath
from scripts.data.store import Datasets
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

    for dataset in datasets.sets:
        dataset.fastq_files = dataset.relative_fastq_path()

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
    metadata: list[list[str]],
    pairwised: dict[Pair],
    ctn_fastq_path: Path,
    id_prefix: str = "id",
) -> tuple[list, list]:
    metadata_table = [["#SampleID", *metadata[0]]]
    for i, row in enumerate(metadata[1:], start=1):
        id_name = id_prefix + str(i)
        metadata_table.append([id_name, *row[1:]])

    manifest_table = [
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"]
    ]
    for i, key in enumerate([row[0] for row in metadata[1:]], start=1):
        id_name = id_prefix + str(i)
        manifest_table.append(
            [
                id_name,
                str(ctn_fastq_path / pairwised[key].forward),
                str(ctn_fastq_path / pairwised[key].reverse),
            ]
        )

    return metadata_table, manifest_table


def write_tsv(path: Path, table: list[list[str]]) -> None:
    with path.open("w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(table)


def create_Mfiles(
    local_output: Path,
    container_fastq_path: Path,
    data: Datasets,
    id_prefix: str = "id",
) -> tuple[Path, Path]:
    """
    Create metadata and manifest files from the given data.
    """

    metadata = combine_all_metadata(data)
    pairwised = pairwise(data)

    metatable, manifest = linked_table_expose(
        metadata, pairwised, container_fastq_path, id_prefix
    )

    metatable_local_path = local_output / "metadata.tsv"
    manifest_local_path = local_output / "manifest.tsv"
    write_tsv(metatable_local_path, metatable)
    write_tsv(manifest_local_path, manifest)

    return metatable_local_path, manifest_local_path
