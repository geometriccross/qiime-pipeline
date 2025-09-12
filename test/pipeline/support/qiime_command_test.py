import pytest
from scripts.pipeline.support import Q2CmdAssembly


def test_Q2CmdAssembly_instance_concatinate_with_incorrect_base_command():
    with pytest.raises(ValueError):
        Q2CmdAssembly("qiime tools import") + Q2CmdAssembly("qiime tools export")
