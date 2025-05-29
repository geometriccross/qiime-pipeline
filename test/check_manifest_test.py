from scripts.check_manifest import extract_filename, extract_first_underscore


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
