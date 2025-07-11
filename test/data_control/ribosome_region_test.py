from scripts.data_control.ribosome_regions import Region


def test_region_initialization():
    """Test the initialization of the Region class."""
    region = Region(
        name="TestRegion",
        trim_left_f=10,
        trim_left_r=15,
        trunc_len_f=200,
        trunc_len_r=200,
    )
    assert region.name == "TestRegion"
    assert region.trim_left_f == 10
    assert region.trim_left_r == 15
    assert region.trunc_len_f == 200
    assert region.trunc_len_r == 200


def test_conversion_to_toml():
    """Test the conversion of the Region object to a TOML document."""
    region = Region(
        name="TestRegion",
        trim_left_f=10,
        trim_left_r=15,
        trunc_len_f=200,
        trunc_len_r=200,
    )
    toml_doc = region.to_toml()

    assert toml_doc["name"] == "TestRegion"
    assert toml_doc["trim_left_f"] == 10
    assert toml_doc["trim_left_r"] == 15
    assert toml_doc["trunc_len_f"] == 200
    assert toml_doc["trunc_len_r"] == 200
