from scripts.pipeline.support import Q2CmdAssembly


def test_Q2CmdAssembly_convert_to_str():
    assembly = Q2CmdAssembly("qiime tools import")
    assert str(assembly) == "qiime tools import"
