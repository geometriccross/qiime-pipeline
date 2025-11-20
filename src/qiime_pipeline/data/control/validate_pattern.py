from re import search
from enum import Enum
from pathlib import Path, PurePath

# pattern.replace(".fastq", "").replace(".gz", "").split("_")[0]


class Direction(Enum):
    Forward = "forward"
    Reverse = "reverse"
    NotMatched = "not_matched"


class Pattern(Enum):
    NotMatched = False
    ILLUMINA = 1
    SRA = 2


def is_illumina_pattern(pattern: str) -> bool:
    return "_R1" in pattern or "_R2" in pattern


def is_sra_pattern(pattern: str) -> bool:
    return "_1.fast" in pattern or "_2.fast" in pattern


def extract_filename(row: dict) -> tuple[str, str]:
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
    return string.replace(".fastq", "").replace(".gz", "").split("_")[0].lower()


def check_direction(string: str) -> Direction:
    """
    Extract the index from the string.
    """
    result = search(r".*_R[12]", string)
    if result is None:
        return Direction.NotMatched
    elif result.group(0).endswith("_R1"):
        return Direction.Forward
    elif result.group(0).endswith("_R2"):
        return Direction.Reverse


def extract_pattern(row: dict) -> tuple[str, str]:
    """
    Extract the forward and reverse file names from the row.
    """
    forward_path = row["forward-absolute-filepath"]
    reverse_path = row["reverse-absolute-filepath"]
    forward_name = PurePath(forward_path).name
    reverse_name = PurePath(reverse_path).name
    return forward_name, reverse_name


def validate_pattern(pattern) -> Pattern:
    """
    Validate the forward and reverse file names.
    """
    if is_illumina_pattern(pattern):
        return Pattern.ILLUMINA
    elif is_sra_pattern(pattern):
        return Pattern.SRA
    else:
        return Pattern.NotMatched


def check_current_pair(fwd: str, rvs: str) -> bool:
    """
    Check if the forward and reverse file names match.
    """
    same_pattern = validate_pattern(fwd) == validate_pattern(rvs)
    same_tag = extract_first_underscore(fwd) == extract_first_underscore(rvs)
    current_direction = (
        check_direction(fwd) is Direction.Forward
        and check_direction(rvs) is Direction.Reverse
    )
    return same_pattern and same_tag and current_direction
