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
from typing import Generator


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


def setup() -> Generator[tuple[SettingData, Executor], None, None]:
    args = argument_parser().parse_args()

    ctn_workspace = Path("/workspace")
    ctn_data = ContainerData(
        image_or_dockerfile=args.image,
        workspace_path=ctn_workspace,
        output_path=PairPath(
            local_pos=args.local_output,
            ctn_pos=ctn_workspace.joinpath("out"),
        ),
        database_path=PairPath(
            local_pos=args.local_database,
            ctn_pos=ctn_workspace.joinpath("/db").joinpath(args.local_database.name),
        ),
    )
    setting = SettingData(
        ctn_data=ctn_data,
        datasets=setup_datasets(args),
        sampling_depth=args.sampling_depth,
    )

    provider = Provider(
        image=ctn_data.image_or_dockerfile,
        mounts=setting.datasets.mounts(setting.workspace_path),
        workspace=ctn_data.workspace_path,
    )

    # provider = Provider.from_dockerfile(
    #     setting.dockerfile,
    #     mounts=setting.datasets.mounts,
    #     workspace=setting.workspace_path,
    #     remove=True,
    # )

    yield setting, Executor(provider.provide())
