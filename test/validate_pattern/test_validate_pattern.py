import pytest
from validate_pattern import *


def test_is_illumina_pattern():
    assert is_illumina_pattern("ACGTACGT")
    assert not is_illumina_pattern("ACGTACGZ")
    assert not is_illumina_pattern("ACGTACG")
    assert not is_illumina_pattern("ACGTACGTX")
