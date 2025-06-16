from pathlib import Path, PurePath


def extract_filename(row: dict) -> str:
    """
    Extract the filename from the row.
    """
    forward_path = row["forward-absolute-filepath"]
    reverse_path = row["reverse-absolute-filepath"]
    forward_name = Path(forward_path).name
    reverse_name = Path(reverse_path).name
    return forward_name, reverse_name


def extract_first_underscore(string: str) -> str:
    """
    Extract the sample name from the row.
    """
    return string.replace(".fastq", "").replace(".gz", "").split("_")[0]


def extract_pattern(row: dict) -> tuple[str, str]:
    """
    Extract the forward and reverse file names from the row.
    """
    forward_path = row["forward-absolute-filepath"]
    reverse_path = row["reverse-absolute-filepath"]
    forward_name = PurePath(forward_path).name
    reverse_name = PurePath(reverse_path).name
    return forward_name, reverse_name


def validate_pattern(forward: str, reverse: str) -> bool:
    """
    Validate the forward and reverse file names.
    """

    return forward == reverse
