#!/usr/bin/env python

from tempfile import NamedTemporaryFile
from pathlib import Path
import pytest
from scripts.data.store.dataset import Datasets
from scripts.data.control.create_Mfiles import (
    search_fastq,
    get_header,
    header_replaced,
    create_Mfiles,
)


def test_search_fastq_success():
    """search_fastq関数の正常系テスト"""
    # テストデータ
    test_files = [
        "/path/to/sample1_R1_001.fastq.gz",
        "/path/to/sample1_R2_001.fastq.gz",
        "/path/to/sample2_R1_001.fastq.gz",
    ]

    # テスト実行
    fwd, rvs = search_fastq("sample1", test_files)

    # 検証
    assert fwd.endswith("sample1_R1_001.fastq.gz")
    assert rvs.endswith("sample1_R2_001.fastq.gz")


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


def test_header_replaced_success():
    """header_replaced関数の正常系テスト"""

    header = ["SampleID", "col1", "col2"]
    result = header_replaced(header, "id")

    assert isinstance(result, list)
    assert len(result) == 1  # 1行のみ（ヘッダー行）
    assert result[0] == ["id", "RawID", "col1", "col2"]


def test_createMfiles_is_currently_create_files(temporary_dataset):
    meta_file = NamedTemporaryFile(delete=True, mode="w+", newline="")
    meta_file.write("#SampleID,feature1,feature2")
    meta_file.write("id1,abc,def")
    mani_file = NamedTemporaryFile(delete=True, mode="w+", newline="")
    test_data = Datasets(sets={temporary_dataset})

    create_Mfiles(
        id_prefix="test_id",
        out_meta=meta_file.name,
        out_mani=mani_file.name,
        data=test_data,
    )

    assert (
        Path(mani_file.name).read_text()
        == "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
    )
