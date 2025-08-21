#!/usr/bin/env python
import pytest
import tempfile
import os
from scripts.data.control.extract_id import extract_id


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


def test_basic_extract(basic_test_data):
    """基本的なID抽出のテスト"""
    # sample1とsample2を抽出
    result = extract_id(basic_test_data, ["sample1", "sample2"])
    assert "sample1" in result
    assert "sample2" in result
    assert "sample3" not in result
    assert "sample4" not in result
    assert result.count("\n") == 2


def test_column_based_extract(species_test_data):
    """カラムベースの抽出テスト"""
    # Species列（インデックス1）からctenocephalides_felisを抽出
    result = extract_id(species_test_data, ["ctenocephalides_felis"], column=1)
    assert "CF001" in result
    assert "CF002" in result
    assert "BF001" not in result
    assert "BF002" not in result
    assert result.count("\n") == 2


def test_exclude_mode(basic_test_data):
    """除外モードのテスト"""
    # sample1とsample2を除外
    result = extract_id(basic_test_data, ["sample1", "sample2"], exclude_mode=True)
    assert "sample1" not in result
    assert "sample2" not in result
    assert "sample3" in result
    assert "sample4" in result
    assert result.count("\n") == 2


def test_invalid_column(basic_test_data):
    """無効な列インデックスのテスト"""
    # 存在しない列（10）を指定
    result = extract_id(basic_test_data, ["sample1"], column=10)
    assert result.count("\n") == 0
