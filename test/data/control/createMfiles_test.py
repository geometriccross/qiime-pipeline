#!/usr/bin/env python

from pathlib import Path
import pytest
from tempfile import TemporaryDirectory
from scripts.data.control.create_Mfiles import (
    search_fastq,
    get_header,
    create_Mfiles,
    combine_all_metadata,
    add_id,
)


def test_search_fastq_correctly_pickup_pair_file():
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample2_R1_001.fastq.gz",
    ]

    fwd, rvs = search_fastq("sample1", test_files)

    # 検証
    assert fwd.name == "sample1_R1_001.fastq.gz"
    assert rvs.name == "sample1_R2_001.fastq.gz"


def test_search_fastq_duplicate_error():
    """search_fastq関数の異常系テスト - ファイルが3つ以上存在する場合"""
    # テストデータ - 同じプレフィックスを持つファイルが3つある
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample1_R3_001.fastq.gz",  # 余分なファイル
    ]

    # エラーが発生することを確認
    with pytest.raises(SyntaxError) as exc_info:
        search_fastq("sample1", test_files)

    # エラーメッセージに該当ファイルが含まれていることを確認
    assert "同名のファイルが3つ以上存在しています" in str(exc_info.value)


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
