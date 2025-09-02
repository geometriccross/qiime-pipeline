#!/usr/bin/env python

from pathlib import Path, PurePath
import pytest
from tempfile import TemporaryDirectory
from scripts.data.control.validate_pattern import extract_first_underscore
from scripts.data.control.create_Mfiles import (
    search_fastq_pair,
    get_header,
    create_Mfiles,
    combine_all_metadata,
    parwised_files,
    linked_table_expose,
    add_id,
    Pair,
)


def test_search_fastq_correctly_pickup_pair_file():
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample2_R1_001.fastq.gz",
    ]

    fwd, rvs = search_fastq_pair("sample1", test_files)

    # 検証
    assert fwd.name == "sample1_R1_001.fastq.gz"
    assert rvs.name == "sample1_R2_001.fastq.gz"


def test_search_fastq_duplicate_error():
    """search_fastq_pair関数の異常系テスト - ファイルが3つ以上存在する場合"""
    # テストデータ - 同じプレフィックスを持つファイルが3つある
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample1_R3_001.fastq.gz",  # 余分なファイル
    ]

    # エラーが発生することを確認
    with pytest.raises(SyntaxError) as exc_info:
        search_fastq_pair("sample1", test_files)

    # エラーメッセージに該当ファイルが含まれていることを確認
    assert "同名のファイルが3つ以上存在しています" in str(exc_info.value)


def test_parwised_files():
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample2_R1_001.fastq.gz",
        "/path/to/sample2_R2_001.fastq.gz",
    ]

    result = parwised_files(test_files)

    assert (
        len(result) == len(test_files) / 2
    ), "テストファイル数と結果のペア数が一致しません。"
    for key in result.keys():
        assert isinstance(result[key], Pair)

        assert PurePath(result[key].forward).name == f"{key}_R1_001.fastq.gz"
        assert PurePath(result[key].reverse).name == f"{key}_R2_001.fastq.gz"


def test_linked_table_expose(dummy_datasets):
    all_fastq = []
    for dataset in dummy_datasets.sets:
        all_fastq.extend(dataset.fastq_files)

    pairwised = parwised_files(all_fastq)
    metadata = combine_all_metadata(dummy_datasets)

    metatable, manifest = linked_table_expose(metadata, pairwised)

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

        assert extract_first_underscore(prob_fwd) == extract_first_underscore(
            prob_rvs
        ), f"{i}行目のファイルパスがペアになっていません。"


def test_get_header_success(tmp_path):
    """get_header関数の正常系テスト"""
    # テスト用のメタデータファイルを作成
    meta_file = tmp_path / "test_meta.csv"
    meta_file.write_text("#SampleID,col1,col2\n")

    # テスト実行
    headers = get_header(str(meta_file))

    # 検証
    assert headers == ["RawID", "col1", "col2"]


def test_get_header_file_not_found():
    """get_header関数の異常系テスト - ファイルが存在しない場合"""
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


def test_add_id(dummy_datasets):
    start = 1

    rows_with_files = combine_all_metadata(dummy_datasets)
    meta, mani = add_id(rows_with_files, "id", start=start)

    assert isinstance(meta, list)
    assert isinstance(mani, list)

    for i, row in enumerate(meta, start=start):
        assert row[0] == f"id{i}"

    for i, row in enumerate(mani, start=start):
        assert row[0] == f"id{i}"


def test_createMfiles_is_currently_creating_files(dummy_datasets):
    with TemporaryDirectory() as temp_dir:
        create_Mfiles(
            id_prefix="test_id",
            out_meta=temp_dir + "/metadata.tsv",
            out_mani=temp_dir + "/manifest.tsv",
            data=dummy_datasets,
        )

        assert Path(temp_dir + "/metadata.tsv").exists()
        assert Path(temp_dir + "/manifest.tsv").exists()
