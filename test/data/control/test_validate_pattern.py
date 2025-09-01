import pytest
from scripts.data.control.validate_pattern import (
    Direction,
    Pattern,
    extract_filename,
    extract_first_underscore,
    check_direction,
    extract_pattern,
    validate_pattern,
    check_current_pair,
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


@pytest.mark.parametrize(
    ["string", "expected"],
    [
        pytest.param("sample1_R1.fastq.gz", Direction.Forward, id="with_R1"),
        pytest.param("sample1_R2.fastq.gz", Direction.Reverse, id="with_R2"),
        pytest.param("sample1.fastq.gz", Direction.NotMatched, id="no_R"),
        pytest.param("sample1_R1_extra.fastq.gz", Direction.Forward, id="extra_R1"),
    ],
)
def test_extract_index(string, expected):
    assert check_direction(string) == expected


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
        pytest.param("t1_R1_001.fastq.gz\n", Pattern.ILLUMINA),
        pytest.param("\tt1_R2_001.fasta", Pattern.ILLUMINA),
        pytest.param("SRR20014836_1.fastq.gz", Pattern.SRA),
        pytest.param("hogehoge.fastq", Pattern.NotMatched),
        pytest.param("\nSAMPLE\n", Pattern.NotMatched),
    ],
)
def test_validate_pattern(pattern, expected):
    assert validate_pattern(pattern) is expected


@pytest.mark.parametrize(
    ["fwd", "rvs", "expected"],
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
def test_check_current_pair(fwd, rvs, expected):
    checked = check_current_pair(fwd, rvs)
    assert (
        checked is expected
    ), f"Expected {expected} but got {checked} for fwd: {fwd}, rvs: {rvs}"
