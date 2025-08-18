import pytest
from scripts.executor import Executor, Provider
from python_on_whales import docker, Container


@pytest.fixture
def trusted_provider():
    provider = Provider(image="alpine", remove=True)

    yield provider

    docker.container.remove(provider.provide(), force=True)


def test_provider():
    provider = Provider(image="alpine")
    assert isinstance(provider, Provider)
    assert isinstance(provider.provide(), Container)


@pytest.mark.parametrize("remove, expected", [(False, "exited"), (True, "absent")])
def test_provider_container_status(remove, expected):
    container = Provider(image="alpine", remove=remove).provide()

    assert Provider.get_status(container) == "running"
    container.stop()
    assert Provider.get_status(container) == expected


@pytest.mark.parametrize(
    "command,expected_out,expected_err",
    [
        (["echo", "Hello World!"], "Hello World!", ""),
    ],
)
def test_command_execution(
    trusted_provider, command: list, expected_out: str, expected_err: str
):
    with Executor(trusted_provider.provide()) as executor:
        output, err = executor.run(command)
        assert output == expected_out
        assert err == expected_err


def test_command_execution_when_cmd_is_failed(trusted_provider):
    with Executor(trusted_provider.provide()) as executor:
        output, err = executor.run(["NonExistingCmd"])
        assert output == ""
        assert err != ""
        assert len(err) > 0
