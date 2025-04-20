#!/usr/bin/env python
from typing import List, Dict
import pytest
from docker.models.containers import Container


def verify_output_contains_ids(output: str, expected_ids: List[str]) -> None:
    """出力に期待されるIDが含まれているか検証する

    Args:
        output: コマンドの出力
        expected_ids: 期待されるIDのリスト
    """
    for id_ in expected_ids:
        assert id_ in output, f"Expected ID '{id_}' not found in output: {output}"


def count_newlines(text: str) -> int:
    """文字列内の改行の数を数える

    Args:
        text: 対象の文字列

    Returns:
        int: 改行の数
    """
    return sum(1 for char in text if char == "\n")


def count_total_lines(file_paths: List[str]) -> int:
    """指定されたファイルの合計行数を計算する

    Args:
        file_paths: 行数を数えるファイルパスのリスト

    Returns:
        int: 合計行数（複数ファイルの場合はヘッダー行を除く）
    """
    total = 0 if len(file_paths) <= 1 else -1  # 複数ファイルの場合はヘッダーを除く
    for path in file_paths:
        with open(path, "r") as f:
            total += len(f.readlines())
    return total


@pytest.mark.parametrize("extract", [["id1", "id2", "id21", "id25"]])
def test_extract_correctly(modified_container: Container, extract: List[str]) -> None:
    """IDによる抽出機能のテスト

    Args:
        extract: 抽出するIDのリスト
    """
    cmd = ["python", "/scripts/extract_id.py", "/tmp/meta"] + extract
    result = modified_container.exec_run(cmd=cmd, demux=True)
    stdout, stderr = result.output
    output = stdout.decode() if stdout else ""
    verify_output_contains_ids(output, extract)


@pytest.mark.parametrize(
    "pattern",
    [
        {"target": ["ctenocephalides_felis"], "origin": ["meta/cat_fleas.csv"]},
        {
            "target": ["ctenocephalides_felis", "ischnopsyllus_needhami"],
            "origin": ["meta/cat_fleas.csv", "meta/bat_fleas.csv"],
        },
    ],
)
def test_column_based_extract(
    modified_container: Container, pattern: Dict[str, List[str]]
) -> None:
    """カラムベースの抽出機能のテスト

    Args:
        pattern: テストパターン（target: 抽出対象、origin: 元ファイル）
    """
    target = pattern["target"]
    origin = pattern["origin"]
    cmd = ["python", "/scripts/extract_id.py", "/tmp/meta", "--column", "3"] + target
    result = modified_container.exec_run(cmd=cmd, demux=True)
    stdout, stderr = result.output
    output = stdout.decode() if stdout else ""

    # 出力の検証
    verify_output_contains_ids(output, target)

    # 行数の検証
    total_lines = count_total_lines(origin)
    actual_lines = count_newlines(output)
    assert (
        total_lines == actual_lines
    ), f"Expected {total_lines} lines in output, but got {actual_lines}"
