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
    # ベース名をキーとした辞書を作成
    file_groups = {}
    for f in files:
        base_name = extract_first_underscore(PurePath(str(f)).name)
        if base_name not in file_groups:
            file_groups[base_name] = []
        file_groups[base_name].append(str(f))

    result = dict()
    # 各グループでペアを作成
    for base_name, group_files in file_groups.items():
        if len(group_files) != 2:
            continue

        file1, file2 = group_files
        try:
            if check_current_pair(file1, file2):
                result[base_name] = Pair(file1, file2)
            elif check_current_pair(file2, file1):
                result[base_name] = Pair(file2, file1)
            else:
                print(f"Warning: Files in group {base_name} don't form a valid pair")
        except Exception as e:
            print(f"Error processing pair {base_name}: {e}")

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
    path.parent.mkdir(parents=True, exist_ok=True)
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
