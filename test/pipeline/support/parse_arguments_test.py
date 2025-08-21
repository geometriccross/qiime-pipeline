import pytest
from pathlib import Path
from scripts.pipeline.support.parse_arguments import parse_pair


@pytest.mark.parametrize(
    "pair_str,expected",
    [
        (
            "metadata_path:fastq_folder",
            [(Path("metadata_path"), Path("fastq_folder"))],
        ),
        (
            "  metadata_path  :  fastq_folder  ",
            [(Path("metadata_path"), Path("fastq_folder"))],
        ),
    ],
)
def test_parse_pair(pair_str, expected):
    """Test the parse_pair function."""
    assert parse_pair(pair_str) == expected


def test_parse_pair_if_give_multiple_pairs():
    """Test if multiple pairs are parsed correctly."""
    pair_str = "metadata1:fastq1,metadata2:fastq2"
    expected = [
        (Path("metadata1"), Path("fastq1")),
        (Path("metadata2"), Path("fastq2")),
    ]
    assert parse_pair(pair_str)[0] == expected[0]


def test_parse_pair_invalid_format():
    """Test if ValueError is raised for invalid pair format."""
    with pytest.raises(ValueError, match="Invalid pair format: invalid_pair"):
        parse_pair("invalid_pair")

    with pytest.raises(ValueError, match="Invalid pair format: metadata_path"):
        parse_pair("metadata_path")

    with pytest.raises(ValueError, match="Invalid pair format: :fastq_folder"):
        parse_pair(":fastq_folder")
