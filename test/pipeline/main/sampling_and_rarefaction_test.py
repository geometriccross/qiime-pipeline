from pathlib import Path
from scripts.data.store.setting_data_structure import SettingData
from scripts.pipeline.support import Executor, Provider
from scripts.pipeline.main.sampling_and_rarefaction import (
    run_rarefaction,
    copy_from_container,
    execute,
)


def test_run_rarefaction(setting: SettingData):
    provider = Provider(
        image="quay.io/qiime2/amplicon:2024.10",
        mounts=setting.datasets.mounts(Path("/data")),
        workspace=setting.workspace_path,
        remove=True,
    )

    executor = Executor(provider.provide())
    run_rarefaction(
        setting=setting,
        executor=executor,
    )
