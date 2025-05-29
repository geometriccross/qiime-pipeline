#!/usr/bin/env python

import pytest
from pathlib import Path  # noqa: F401
from scripts.check_manifest import ManifestChecker, ManifestError


@pytest.fixture
def valid_manifest(tmp_path):
    """有効なマニフェストファイルを作成するfixture"""
    manifest_path = tmp_path / "manifest.tsv"
    # テスト用の一時ファイルを作成
    forward_file = tmp_path / "sample1_R1.fastq"
    reverse_file = tmp_path / "sample1_R2.fastq"
    forward_file.touch()
    reverse_file.touch()

    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        f"sample1\t{forward_file}\t{reverse_file}"
    )
    manifest_path.write_text(manifest_content)
    return manifest_path


@pytest.fixture
def invalid_name_manifest(tmp_path):
    """ファイル名が不一致のマニフェストファイルを作成するfixture"""
    manifest_path = tmp_path / "manifest.tsv"
    # テスト用の一時ファイルを作成
    forward_file = tmp_path / "sample1_R1.fastq"
    reverse_file = tmp_path / "sample2_R2.fastq"  # 意図的に異なる名前
    forward_file.touch()
    reverse_file.touch()

    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        f"sample1\t{forward_file}\t{reverse_file}"
    )
    manifest_path.write_text(manifest_content)
    return manifest_path


def test_valid_manifest(valid_manifest):
    """正常なマニフェストファイルの検証"""
    checker = ManifestChecker(str(valid_manifest))
    checker.validate()  # 例外が発生しないことを確認


def test_missing_file():
    """存在しないマニフェストファイルの検証"""
    with pytest.raises(FileNotFoundError) as e:
        checker = ManifestChecker("not_exists.tsv")
        checker.validate()
    assert "マニフェストファイルが見つかりません" in str(e.value)


def test_invalid_file_names(invalid_name_manifest):
    """ファイル名の不一致の検証"""
    checker = ManifestChecker(str(invalid_name_manifest))
    with pytest.raises(ManifestError) as e:
        checker.validate()
    assert "が一致しません" in str(e.value)


def test_missing_headers(tmp_path):
    """必要なヘッダーが不足している場合の検証"""
    manifest_path = tmp_path / "manifest.tsv"
    manifest_content = "wrong-header1\twrong-header2\n" "value1\tvalue2"
    manifest_path.write_text(manifest_content)

    checker = ManifestChecker(str(manifest_path))
    with pytest.raises(ManifestError) as e:
        checker.validate()
    assert "マニフェストファイルの形式が不正です" in str(e.value)


def test_missing_data_files(tmp_path):
    """参照されるファイルが存在しない場合の検証"""
    manifest_path = tmp_path / "manifest.tsv"
    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        "sample1\t/not/exists/forward.fastq\t/not/exists/reverse.fastq"
    )
    manifest_path.write_text(manifest_content)

    checker = ManifestChecker(str(manifest_path))
    with pytest.raises(ManifestError) as e:
        checker.validate()
    assert "forward-absolute-filepath が存在しません" in str(e.value)
    assert "reverse-absolute-filepath が存在しません" in str(e.value)


def test_invalid_csv_format(tmp_path):
    """不正なCSVフォーマットの検証"""
    manifest_path = tmp_path / "manifest.tsv"
    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        "sample1\tpath1\tpath2\textra_column\tmore_columns"  # 余分な列があり、CSVフォーマットが不正
    )
    manifest_path.write_text(manifest_content)

    checker = ManifestChecker(str(manifest_path))
    with pytest.raises(ManifestError) as e:
        checker.validate()
    assert "マニフェストファイルの形式が不正です" in str(e.value)
