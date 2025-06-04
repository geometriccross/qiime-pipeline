import docker
from scripts.executor import Executor


def test_executor_create_instance(container: docker.models.containers.Container):
    ctn = container("alpine")

    executor = Executor(ctn)
    assert isinstance(executor, Executor)
    assert executor.status() == "created"


def test_executor_start_and_stop(container: docker.models.containers.Container):
    ctn = container("alpine")

    with Executor(ctn) as executor:
        assert executor.status() == "running"

    assert executor.status() == "removing"
