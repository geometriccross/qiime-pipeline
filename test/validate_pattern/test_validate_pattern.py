import pytest
from scripts.validate_pattern.validate_pattern import (
    Pattern,
    extract_filename,
    extract_first_underscore,
    extract_pattern,
    validate_pattern,
)


def test_can_extract_filename_from_manifest_row():
    row = {
        "forward-absolute-filepath": "/path/to/sample1_R1.fastq.gz",
        "reverse-absolute-filepath": "/path/to/sample1_R2.fastq.gz",
    }
    forward_name, reverse_name = extract_filename(row)
    assert forward_name == "sample1_R1.fastq.gz"
    assert reverse_name == "sample1_R2.fastq.gz"


def test_can_extract_first_underscore_from_string():
    # Ba-fle2_S7_L001_R1_001.fastq.gz
    string = "sample1_R1.fastq.gz"
    sample_name = extract_first_underscore(string)
    assert sample_name == "sample1"

    string_with_no_underscore = "sample1.fastq.gz"
    sample_name_no_underscore = extract_first_underscore(string_with_no_underscore)
    assert sample_name_no_underscore == "sample1"

    string_with_multiple_underscores = "sample1_R1_extra.fastq.gz"
    sample_name_multiple = extract_first_underscore(string_with_multiple_underscores)
    assert sample_name_multiple == "sample1"


def test_extract_pattern():
    row = {
        "forward-absolute-filepath": "t1_R1.fastq.gz",
        "reverse-absolute-filepath": "t1_R2.fastq.gz",
    }
    forward, reverse = extract_pattern(row)
    assert forward == "t1_R1.fastq.gz"
    assert reverse == "t1_R2.fastq.gz"


@pytest.mark.parametrize(
    ["pattern", "expected"],
    [
        pytest.param("t1_R1_.fastq.gz", Pattern.ILLUMINA),
        pytest.param("t1_R2.fasta", Pattern.ILLUMINA),
        pytest.param("SRR20014836_1.fastq.gz", Pattern.SRA),
        pytest.param("hogehoge.fastq", Pattern.NotMatched),
    ],
)
def test_validate_pattern(pattern, expected):
    assert validate_pattern(pattern) is expected


# @pytest.mark.parametrize(
#     ["forward", "reverse", "expected"],
    [
        pytest.param(
            "t1_R1.fastq.gz",
            "t1_R2.fastq.gz",
            True,
            id="current pattern, same sample and foward/reverse",
        ),
        pytest.param(
            "t1_R1.fastq.gz",
            "t2_R2.fastq.gz",
            False,
            id="wrong_pattern, different sample specified",
        ),
        pytest.param(
            "t1_R1.fastq.gz",
            "t1_R1.fastq.gz",
            False,
            id="wrong_pattern, specified same file for both",
        ),
        pytest.param(
            "t1_R2.fastq.gz",
            "t2_R1.fastq.gz",
            False,
            id="wrong_pattern, sample specificaiton is shifted",
        ),
    ],
)
def test_validate_pattern(forward, reverse, expected):
    f, r = extract_pattern(
        {
            "forward-absolute-filepath": forward,
            "reverse-absolute-filepath": reverse,
        }
    )

    assert (
        validate_pattern(f, r) is expected
    ), f"Failed for forward: {forward}, reverse: {reverse}"
