#!/usr/bin/env python

import sys
import pytest
from pathlib import Path
from scripts.check_manifest import validate_manifest


def create_manifest_file(tmp_path: Path, content: str) -> Path:
    """マニフェストファイルを作成する

    Args:
        tmp_path: 一時ディレクトリのパス
        content: マニフェストファイルの内容

    Returns:
        Path: 作成されたマニフェストファイルのパス
    """
    manifest_path = tmp_path / "manifest.tsv"
    manifest_path.write_text(content)
    return manifest_path


@pytest.fixture
def valid_manifest(tmp_path):
    """有効なマニフェストファイルをセットアップするfixture"""
    # テスト用のfastqファイルを作成
    fastq_dir = tmp_path / "fastq"
    fastq_dir.mkdir()
    forward = fastq_dir / "sample1_R1.fastq"
    reverse = fastq_dir / "sample1_R2.fastq"
    forward.touch()
    reverse.touch()

    # マニフェストファイルの作成
    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        f"sample1\t{forward}\t{reverse}"
    )
    return create_manifest_file(tmp_path, manifest_content)


def test_valid_manifest(valid_manifest):
    """正常なマニフェストファイルの検証"""
    validate_manifest(str(valid_manifest))  # 例外が発生しないことを確認


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "description": "不正なフォーマット（余分な列）",
            "content": (
                "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
                "sample1\tpath1\tpath2\textra"
            ),
            "expected_error": "マニフェストファイルの形式が不正です",
        },
        {
            "description": "ヘッダー不足",
            "content": (
                "wrong-header1\twrong-header2\twrong-header3\n" "sample1\tpath1\tpath2"
            ),
            "expected_error": "必要なヘッダーが不足しています",
        },
    ],
)
def test_invalid_format(tmp_path, test_case, capsys):
    """不正なフォーマットのテスト"""
    manifest_path = create_manifest_file(tmp_path, test_case["content"])

    with pytest.raises(SystemExit) as excinfo:
        validate_manifest(str(manifest_path))

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert test_case["expected_error"] in captured.err


def test_missing_files(tmp_path, capsys):
    """存在しないファイルを参照している場合のテスト"""
    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        "sample1\t/not/exists/forward.fastq\t/not/exists/reverse.fastq"
    )
    manifest_path = create_manifest_file(tmp_path, manifest_content)

    with pytest.raises(SystemExit) as excinfo:
        validate_manifest(str(manifest_path))

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "が存在しません" in captured.err


def test_allow_missing_files(tmp_path):
    """--allow-missingオプションのテスト"""
    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        "sample1\t/not/exists/data_R1.fastq\t/not/exists/data_R2.fastq"
    )
    manifest_path = create_manifest_file(tmp_path, manifest_content)
    validate_manifest(
        str(manifest_path), allow_missing=True
    )  # 例外が発生しないことを確認


def test_inconsistent_file_names(tmp_path, capsys):
    """ファイル名が不一致の場合のテスト"""
    # テストファイルの作成
    fastq_dir = tmp_path / "fastq"
    fastq_dir.mkdir()
    (fastq_dir / "sample1_R1.fastq").touch()
    (fastq_dir / "sample2_R2.fastq").touch()  # 意図的に異なる名前

    manifest_content = (
        "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n"
        f"sample1\t{fastq_dir}/sample1_R1.fastq\t{fastq_dir}/sample2_R2.fastq"
    )
    manifest_path = create_manifest_file(tmp_path, manifest_content)

    with pytest.raises(SystemExit) as excinfo:
        validate_manifest(str(manifest_path))

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "が一致しません" in captured.err


def test_command_line_interface(valid_manifest):
    """コマンドラインインターフェースのテスト"""
    import subprocess

    # 正常系のテスト
    cmd = [sys.executable, "scripts/check_manifest.py", str(valid_manifest)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert not result.stderr

    # --allow-missingオプションのテスト
    cmd = [
        sys.executable,
        "scripts/check_manifest.py",
        "--allow-missing",
        str(valid_manifest),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert not result.stderr
