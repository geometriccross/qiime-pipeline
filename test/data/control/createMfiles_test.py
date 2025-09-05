#!/usr/bin/env python

from pathlib import Path, PurePath
import pytest
from scripts.data.control.validate_pattern import extract_first_underscore
from scripts.data.control.create_Mfiles import (
    Pair,
    get_header,
    combine_all_metadata,
    pairwised_files,
    pairwise,
    linked_table_expose,
)


def test_get_header_success(tmp_path):
    # テスト用のメタデータファイルを作成
    meta_file = tmp_path / "test_meta.csv"
    meta_file.write_text("#SampleID,col1,col2\n")

    # テスト実行
    headers = get_header(str(meta_file))

    # 検証
    assert headers == ["RawID", "col1", "col2"]


def test_get_header_file_not_found():
    # 存在しないファイルパスでテスト
    with pytest.raises(AssertionError) as exc_info:
        get_header("/path/to/nonexistent/file.csv")

    # エラーメッセージを確認
    assert "does not exist" in str(exc_info.value)


def test_combine_all_metadata(dummy_datasets):
    table = combine_all_metadata(dummy_datasets)
    assert len(table) == len(dummy_datasets.sets) + 1

    for i, row in enumerate(table):
        assert len(row) == len(table[0]), f"{i}行目のカラム数が異なります。"

    pre = None
    for i, row in enumerate(table[1:]):
        if pre is None:
            pre = row
            continue

        after = row
        assert pre[0] < after[0], f"{i}行目のIDが昇順ではありません。"


def test_pairwised_files():
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample2_R1_001.fastq.gz",
        "/path/to/sample2_R2_001.fastq.gz",
    ]

    result = pairwised_files(test_files)

    assert (
        len(result) == len(test_files) / 2
    ), "テストファイル数と結果のペア数が一致しません。"
    for key in result.keys():
        assert isinstance(result[key], Pair)

        assert PurePath(result[key].forward).name == f"{key}_R1_001.fastq.gz"
        assert PurePath(result[key].reverse).name == f"{key}_R2_001.fastq.gz"


def test_linked_table_expose(dummy_datasets):
    pairwised = pairwise(dummy_datasets)
    metadata = combine_all_metadata(dummy_datasets)
    ctn_fastq_path = Path("/container/path/to/fastq")

    metatable, manifest = linked_table_expose(metadata, pairwised, ctn_fastq_path)

    assert isinstance(metatable, list)
    assert isinstance(manifest, list)

    assert len(metatable[0]) == len(metadata[0]) + 1
    assert len(metatable) == len(manifest)

    for i in range(len(metatable)):
        if i == 0:
            continue

        assert metatable[i][0] == f"id{i}"
        assert manifest[i][0] == f"id{i}"

    # manifestの構造を検証
    for i in range(len(manifest)):
        if i == 0:
            continue

        prob_fwd = manifest[i][1]
        prob_rvs = manifest[i][2]
        assert "R1" in prob_fwd
        assert "R2" in prob_rvs

        assert prob_fwd.startswith(str(ctn_fastq_path))
        assert prob_rvs.startswith(str(ctn_fastq_path))

        assert extract_first_underscore(prob_fwd) == extract_first_underscore(
            prob_rvs
        ), f"{i}行目のファイルパスがペアになっていません。"
