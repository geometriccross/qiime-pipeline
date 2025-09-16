from pathlib import Path
import pytest
from tempfile import NamedTemporaryFile
from scripts.pipeline.support.executor import Executor, Provider
from python_on_whales import Container


@pytest.fixture(scope="module")
def trusted_provider():
    provider = Provider(image="alpine", remove=True)

    yield provider


@pytest.fixture(scope="module")
def shared_container(trusted_provider):
    container = trusted_provider.provide()
    yield container
    container.stop()


def test_provider_from_dockerfile():
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
def test_provider_is_currently_create_instance_and_container_status(remove, expected):
    provider = Provider(image="alpine", remove=remove)
    assert isinstance(provider, Provider)

    container = provider.provide()
    assert isinstance(container, Container)
    assert container.exists()

    try:
        assert Provider.get_status(container) == "running"
        container.stop()
        assert Provider.get_status(container) == expected
    finally:
        container.remove(force=True)


@pytest.mark.parametrize(
    "command,expected_out,expected_err",
    [
        (["echo", "Hello World!"], "Hello World!", ""),
    ],
)
def test_command_execution(
    shared_container, command: list[str], expected_out: str, expected_err: str
):
    with Executor(shared_container) as executor:
        output = executor.run(command)
        assert output == expected_out


def test_command_execution_when_command_is_failed(shared_container):
    with Executor(shared_container) as executor:
        pytest.raises(RuntimeError, executor.run, ["NonExistingCmd"])
