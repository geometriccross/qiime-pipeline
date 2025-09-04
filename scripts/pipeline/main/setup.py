from pathlib import Path
from typing import Tuple
from argparse import Namespace
from scripts.data.control.check_manifest import check_manifest
from scripts.data.control.create_Mfiles import create_Mfiles
from scripts.data.store.dataset import Datasets, Dataset
from scripts.data.store.setting_data_structure import (
    ContainerData,
    SettingData,
    PairPath,
)
from scripts.data.store.ribosome_regions import V3V4
from scripts.pipeline.support.executor import Executor, Provider
from scripts.pipeline.support.parse_arguments import argument_parser


def setup_files(output: Path, datasets: Datasets) -> Tuple[Path, Path]:
    create_Mfiles(
        id_prefix="id",
        out_meta=(metafile := output / "metadata.csv"),
        out_mani=(manifest := output / "manifest.csv"),
        data=datasets,
    )

    if not check_manifest(manifest):
        raise ValueError("Manifest file is invalid")

    return Path(metafile), Path(manifest)


def setup_datasets(arg: Namespace) -> Datasets:
    data = []
    for metadata_path, fastq_folder in arg.data:
        # Use the basename of the metadata path as the dataset name
        data.append(
            Dataset(
                name=fastq_folder.stem,
                fastq_folder=fastq_folder,
                metadata_path=metadata_path,
                region=V3V4(),
            )
        )

    return Datasets(sets=set(data))


def setup_config(arg: Namespace) -> SettingData:
    ctn_workspace = Path("/workspace")
    ctn_data = ContainerData(
        image_or_dockerfile=arg.image,
        workspace_path=ctn_workspace,
        output_path=PairPath(
            local_pos=arg.local_output,
            ctn_pos=ctn_workspace.joinpath("out"),
        ),
        database_path=PairPath(
            local_pos=arg.local_database,
            ctn_pos=ctn_workspace.joinpath("/db").joinpath(arg.local_database.name),
        ),
    )
    setting = SettingData(
        ctn_data=ctn_data,
        datasets=setup_datasets(arg),
        sampling_depth=arg.sampling_depth,
    )
    return setting


def setup_executor(setting: SettingData) -> Executor:
    provider = Provider(
        image=setting.ctn_data.image_or_dockerfile,
        mounts=setting.datasets.mounts(setting.workspace_path).joinpath("data"),
        workspace=setting.ctn_data.workspace_path,
    )

    return Executor(provider.provide())


def setup() -> tuple[SettingData, Executor]:
    args = argument_parser().parse_args()
    setting = setup_config(args)
    executor = setup_executor(setting)

    return setting, executor
