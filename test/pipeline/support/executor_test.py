from pathlib import Path
import pytest
from src.pipeline.support.executor import Executor, Provider
from python_on_whales import Container


@pytest.fixture(scope="module")
def shared_container():
    container = Provider(image="alpine", remove=True).provide()

    yield container

    try:
        container.remove(force=True)
        container.stop()
    except Exception:
        pass


def test_provider_from_dockerfile(tmp_path: Path):
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM alpine")

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
