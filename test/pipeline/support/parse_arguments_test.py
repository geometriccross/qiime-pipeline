import pytest
from pathlib import Path
from src.pipeline.support.parse_arguments import parse_pair


@pytest.mark.parametrize(
    "pair_str,expected",
    [
        ("metadata_path:fastq_folder", (Path("metadata_path"), Path("fastq_folder"))),
        (
            "  metadata_path  :  fastq_folder  ",
            (Path("metadata_path"), Path("fastq_folder")),
        ),
    ],
)
def test_parse_pair(pair_str, expected):
    """Test the parse_pair function."""
    assert parse_pair(pair_str) == expected


def test_parse_pair_invalid_format():
    """Test if ValueError is raised for invalid pair format."""
    with pytest.raises(ValueError, match="Invalid pair format: invalid_pair"):
        parse_pair("invalid_pair")

    with pytest.raises(ValueError, match="Invalid pair format: metadata_path"):
        parse_pair("metadata_path")

    with pytest.raises(ValueError, match="Invalid pair format: :fastq_folder"):
        parse_pair(":fastq_folder")
