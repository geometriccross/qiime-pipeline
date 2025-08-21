from pathlib import Path
import pytest
from tempfile import NamedTemporaryFile
from scripts.pipeline.support.executor import Executor, Provider
from python_on_whales import Container


def test_provider():
    provider = Provider(image="alpine")
    assert isinstance(provider, Provider)

    container = provider.provide()
    assert isinstance(container, Container)
    assert container.exists()

    container.stop()


def test_provider_from_dokerfile():
    with NamedTemporaryFile(suffix=".Dockerfile", delete=True) as tmp_file:
        tmp_file.write(b"FROM alpine")
        tmp_file.flush()

        dockerfile_path = Path(tmp_file.name)
        provider = Provider.from_dockerfile(dockerfile_path, remove=True)
        assert isinstance(provider, Provider)

        container = provider.provide()
        assert isinstance(container, Container)
        assert container.exists()

        container.stop()


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


def test_command_execution_when_command_is_failed(trusted_provider):
    with Executor(trusted_provider.provide()) as executor:
        output, err = executor.run(["NonExistingCmd"])
        assert output == ""
        assert err != ""
        assert len(err) > 0
