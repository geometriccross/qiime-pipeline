import datetime
import random
import string
from python_on_whales import docker
from pathlib import Path
from argparse import Namespace
from tomlkit.toml_file import TOMLFile
from scripts.data_store.setting_data_structure import SettingData
from scripts.data_store.dataset import Databank, Dataset
from scripts.data_store.ribosome_regions import V3V4
from scripts.data_control.parse_arguments import argument_parser


def generate_id() -> str:
    """
    Generate a unique ID string in the format: 'mmddHHMMSS_xyz'
    where mm is the month name (lowercase), dd is the day,
    HHMMSS is the time, and xyz is a random 3-character string.

    Returns:
        str: Generated ID string
    """
    now = datetime.datetime.now()
    month = now.strftime("%b").lower()
    datetime_str = now.strftime("%d%H%M%S")

    # Generate random 3 characters (lowercase alphanumeric)
    chars = string.ascii_lowercase + string.digits
    random_str = "".join(random.choices(chars, k=3))

    return f"{month}{datetime_str}_{random_str}"


def setup_databank(arg: Namespace) -> SettingData:
    data = []
    for metadata_path, fastq_folder in arg.data:
        # Use the basename of the metadata path as the dataset name
        data.append(
            Dataset(
                name=metadata_path.basename(),
                fastq_folder=fastq_folder,
                metadata_path=metadata_path,
                region=V3V4(),
            )
        )

    databank = Databank(sets=set(data))

    return SettingData(
        dockerfile=arg.dockerfile,
        sampling_depth=arg.sampling_depth,
        databank=databank,
    )


def arg_factory(workdir: Path, command: list[str]) -> dict:
    # docker execではentorypointを経由せず直接コマンドを実行するためbase環境が認識されない
    # そのためexecを使用する際にはbaseを認識させなければならない
    cmd_line = [
        "micromamba",
        "run",
        "-n",
        "base",
        "bash",
        "-exc",
        f'{" ".join(command)}',
    ]

    return {
        "command": " ".join(cmd_line),
        "workdir": workdir,
        "detach": True,
        "remove": True,
    }


def pipeline_run(setting_data: SettingData):
    if docker.images("qiime").__len__() == 0:
        print("Building Docker image for QIIME...")
        docker.build(
            path=Path("."),
            dockerfile=setting_data.dockerfile,
            tag="qiime",
        )

    ctn_name = "qiime" + generate_id()
    with docker.container.run(
        image="qiime",
        name=ctn_name,
        detach=True,
        remove=True,
        mounts=setting_data.databank.mounts(Path("/data")),
    ) as ctn:
        print(f"Container {ctn_name} is running...")
        ctn.execute(
            **arg_factory(
                workdir=setting_data.workspace_path,
                command="qiime --help".split(),
            )
        )


if __name__ == "__main__":
    args = argument_parser().parse_args()
    setting_data = setup_databank(args)
    TOMLFile(args.output / "settings.toml").write(setting_data.to_toml())

    pipeline_run(setting_data)
