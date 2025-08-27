#!/usr/bin/env python
import pytest
import tempfile
import os
from scripts.data.control.extract_id import extract_id, ExtractError


def create_test_file(content: str) -> str:
    """テスト用の一時ファイルを作成する

    Args:
        content: ファイルの内容

    Returns:
        str: 作成した一時ファイルのパス
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
        f.write(content)
        return f.name


@pytest.fixture
def basic_test_data():
    """基本的なテスト用データを提供する"""
    content = (
        "#SampleID\tSpecies\tLocation\tType\n"
        + "sample1\tspecies_A\tloc1\ttypeX\n"
        + "sample2\tspecies_B\tloc2\ttypeY\n"
        + "sample3\tspecies_A\tloc3\ttypeX\n"
        + "sample4\tspecies_C\tloc1\ttypeZ"
    )
    file_path = create_test_file(content)
    yield file_path
    os.unlink(file_path)


@pytest.fixture
def species_test_data():
    """種名によるテスト用データを提供する"""
    content = (
        "#SampleID\tSpecies\tLocation\tType\n"
        + "CF001\tctenocephalides_felis\tTokyo\tparasite\n"
        + "CF002\tctenocephalides_felis\tOsaka\tparasite\n"
        + "BF001\tischnopsyllus_needhami\tTokyo\tparasite\n"
        + "BF002\tischnopsyllus_needhami\tKyoto\tparasite"
    )
    file_path = create_test_file(content)
    yield file_path
    os.unlink(file_path)


@pytest.fixture
def empty_test_data():
    """空のテストファイルを提供する"""
    file_path = create_test_file("")
    yield file_path
    os.unlink(file_path)


def test_basic_extract(basic_test_data):
    """基本的なID抽出のテスト"""
    # sample1とsample2を抽出
    results = list(extract_id(basic_test_data, ["sample1", "sample2"]))
    assert len(results) == 3  # ヘッダー + 2行
    assert "sample1" in results[1]
    assert "sample2" in results[2]
    assert all("sample3" not in row for row in results)
    assert all("sample4" not in row for row in results)


def test_column_based_extract(species_test_data):
    """カラムベースの抽出テスト"""
    # Species列（インデックス1）からctenocephalides_felisを抽出
    results = list(extract_id(species_test_data, ["ctenocephalides_felis"], column=1))
    assert len(results) == 3  # ヘッダー + 2行
    assert "CF001" in results[1]
    assert "CF002" in results[2]
    assert all("BF001" not in row for row in results)
    assert all("BF002" not in row for row in results)


def test_exclude_mode(basic_test_data):
    """除外モードのテスト"""
    # sample1とsample2を除外
    results = list(
        extract_id(basic_test_data, ["sample1", "sample2"], exclude_mode=True)
    )
    assert len(results) == 3  # ヘッダー + 2行
    assert all("sample1" not in row for row in results[1:])
    assert all("sample2" not in row for row in results[1:])
    assert "sample3" in results[1] or "sample3" in results[2]
    assert "sample4" in results[1] or "sample4" in results[2]


def test_invalid_column(basic_test_data):
    """無効な列インデックスのテスト"""
    # 存在しない列（10）を指定
    with pytest.raises(ExtractError) as exc_info:
        list(extract_id(basic_test_data, ["sample1"], column=10))
    assert "範囲外です" in str(exc_info.value)


def test_empty_file(empty_test_data):
    """空ファイルのテスト"""
    with pytest.raises(ExtractError) as exc_info:
        list(extract_id(empty_test_data, ["sample1"]))
    assert "ファイルが空です" in str(exc_info.value)


def test_file_not_found():
    """存在しないファイルのテスト"""
    with pytest.raises(ExtractError) as exc_info:
        list(extract_id("non_existent_file.tsv", ["sample1"]))
    assert "見つかりません" in str(exc_info.value)


def test_generator_behavior(basic_test_data):
    """ジェネレータの動作テスト"""
    generator = extract_id(basic_test_data, ["sample1"])
    header = next(generator)
    assert "#SampleID" in header

    first_row = next(generator)
    assert "sample1" in first_row

    # これ以上sample1は含まれていないはず
    remaining_rows = list(generator)
    assert all("sample1" not in row for row in remaining_rows)
