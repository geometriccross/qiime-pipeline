#!/usr/bin/env python
import pytest

pytest_plugins = ["container_util"]  # noqa: F401


@pytest.mark.parametrize("extract", [["id1", "id2", "id21", "id25"]])
def test_extract_correctry(container, extract):
    cmd = ["python", "/scripts/extract_id.py", "/tmp/meta"] + extract
    result = container.exec_run(cmd=cmd, demux=True)
    stdout, stderr = result.output
    output = stdout.decode() if stdout else ""
    assert all(id_ in output for id_ in extract), f"Expected IDs not found: {output}"


@pytest.mark.parametrize(
    "pattern",
    [
        {"target": ["ctenocephalides_felis"], "origin": ["meta/cat_fleas.csv"]},
        {
            "target": ["ctenocephalides_felis", "ischnopsyllus_needhami"],
            "origin": ["meta/cat_fleas.csv", "meta/bat_fleas.csv"],
        },
    ],
)
def test_column_based_extract(container, pattern):
    target = pattern["target"]
    origin = pattern["origin"]
    cmd = ["python", "/scripts/extract_id.py", "/tmp/meta", "--column", "3"] + target
    result = container.exec_run(cmd=cmd, demux=True)
    stdout, stderr = result.output
    output = stdout.decode() if stdout else ""
    total_line = 0 if len(origin) <= 1 else -1  # count header
    for path in origin:
        with open(path, "r") as f:
            total_line += len(f.readlines())
    for t in target:
        assert t in output
    assert total_line == output.count("\n")
