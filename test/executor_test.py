import docker
from typing import Callable
from scripts.executor import Executor


def test_executor_create_instance(
    container: Callable[[str], docker.models.containers.Container],
):
    ctn = container("alpine")

    executor = Executor(ctn)
    assert isinstance(executor, Executor)
    assert executor.status() == "created"


def test_executor_start_and_stop(
    container: Callable[[str], docker.models.containers.Container],
):
    ctn = container("alpine")

    with Executor(ctn) as executor:
        assert executor.status() == "running"

    assert executor.status() == "removing"


def test_executor_run_commands(
    container: Callable[[str], docker.models.containers.Container],
):
    # single command execution
    with Executor(container("alpine"), auto_remove=True) as executor:
        output = executor.run("echo Hello, World!")
        assert output.strip() == "Hello, World!"

    # multiple command execution
    with Executor(container("alpine"), auto_remove=True) as executor:
        outputs = executor.run("echo Hello, World!")
        outputs += executor.run("echo Goodbye, World!")
        assert outputs.strip() == "Hello, World!\nGoodbye, World!"
