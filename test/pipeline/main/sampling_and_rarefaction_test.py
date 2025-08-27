import pytest
from scripts.data.store.setting_data_structure import SettingData
from scripts.pipeline.support.executor import Executor, Provider
from scripts.pipeline.main.sampling_and_rarefaction import (
    run_rarefaction,
    copy_from_container,
    execute,
)


@pytest.mark.slow
def test_run_rarefaction(setting: SettingData):
    provider = Provider.from_dockerfile(
        setting.dockerfile,
        mounts=setting.datasets.mounts,
        workspace=setting.workspace_path,
        remove=True,
    )

    executor = Executor(provider.provide())
    run_rarefaction(
        setting=setting,
        executor=executor,
    )
