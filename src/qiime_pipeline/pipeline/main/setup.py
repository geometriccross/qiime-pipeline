from pathlib import Path
from typing import Tuple
from argparse import Namespace
from src.data.control import check_manifest, create_Mfiles
from src.data.store import (
    Datasets,
    Dataset,
    ContainerData,
    SettingData,
    PairPath,
    Regions,
)
from src.pipeline.support import (
    Executor,
    Provider,
    argument_parser,
    PipelineContext,
    PipelineType,
)


def setup_datasets(arg: Namespace) -> Datasets:
    data = []
    for metadata_path, fastq_folder in arg.data:
        # Use the basename of the metadata path as the dataset name
        data.append(
            Dataset(
                name=fastq_folder.stem,
                fastq_folder=fastq_folder,
                metadata_path=metadata_path,
                region=Regions()[arg.dataset_region],
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
        container_data=ctn_data,
        datasets=setup_datasets(arg),
        sampling_depth=arg.sampling_depth,
    )
    return setting


def setup_files(setting: SettingData) -> Tuple[PairPath, PairPath]:
    local_metafile, local_manifest = create_Mfiles(
        local_output=setting.container_data.output_path.local_pos,
        container_fastq_path=(setting.container_data.workspace_path / "data"),
        data=setting.datasets,
    )

    if not check_manifest(local_manifest):
        raise ValueError("Manifest file is invalid")

    def __builder(p: Path) -> PairPath:
        return PairPath(
            local_pos=p, ctn_pos=setting.container_data.workspace_path / p.name
        )

    return __builder(local_metafile), __builder(local_manifest)


def setup_mounts(
    metafile_pairpath: PairPath,
    manifest_pairpath: PairPath,
    db_pairpath: PairPath,
    ctn_workspace_dir: Path,
    datasets: Datasets,
) -> list[str]:

    def __convert_path_into_mount_format(pairpath: PairPath):
        return [
            "type=bind",
            f"src={pairpath.local_pos.resolve()}",
            f"dst={pairpath.ctn_pos},readonly",
        ]

    return [
        __convert_path_into_mount_format(metafile_pairpath),
        __convert_path_into_mount_format(manifest_pairpath),
        __convert_path_into_mount_format(db_pairpath),
        *datasets.mounts(ctn_workspace_dir / "data"),
    ]


def setup_executor(mounts: list[str], setting: SettingData) -> Executor:
    provider = Provider(
        image=setting.container_data.image_or_dockerfile,
        name=setting.batch_id,
        mounts=mounts,
        workspace=setting.container_data.workspace_path,
    )

    return Executor(provider.provide())


def setup_context(args: Namespace) -> PipelineContext:
    setting = setup_config(args)

    metadata, manifest = setup_files(setting)
    mounts = setup_mounts(
        metafile_pairpath=metadata,
        manifest_pairpath=manifest,
        ctn_workspace_dir=setting.container_data.workspace_path,
        db_pairpath=setting.container_data.database_path,
        datasets=setting.datasets,
    )
    executor = setup_executor(mounts, setting)

    return PipelineContext(
        ctn_metadata=metadata.ctn_pos,
        ctn_manifest=manifest.ctn_pos,
        executor=executor,
        setting=setting,
        pipeline_type=PipelineType.from_str(args.pipeline),
    )


def setup() -> PipelineContext:
    args = argument_parser().parse_args()
    return setup_context(args)
