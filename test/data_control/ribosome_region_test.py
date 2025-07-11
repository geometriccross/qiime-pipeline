import pytest
from scripts.data_control.ribosome_regions import Region


@pytest.fixture
def region():
    """Fixture to create a Region object for testing."""
    return Region(
        name="TestRegion",
        trim_left_f=10,
        trim_left_r=15,
        trunc_len_f=200,
        trunc_len_r=200,
    )


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


def test_conversion_to_toml(region):
    """Test the conversion of the Region object to a TOML document."""
    toml_doc = region.to_toml()

    assert toml_doc["name"] == "TestRegion"
    assert toml_doc["trim_left_f"] == 10
    assert toml_doc["trim_left_r"] == 15
    assert toml_doc["trunc_len_f"] == 200
    assert toml_doc["trunc_len_r"] == 200


def test_build_from_toml(region):
    """Test the initialization of the Region object from a TOML document."""
    toml_doc = region.to_toml()
    new_region = Region.from_toml(toml_doc)

    assert isinstance(new_region, Region)
    assert new_region.name == "TestRegion"
    assert new_region.trim_left_f == 10
    assert new_region.trim_left_r == 15
    assert new_region.trunc_len_f == 200
    assert new_region.trunc_len_r == 200
