import datetime
import random
import string
from pathlib import Path
from scripts.data_control.dataset import Databank
from scripts.data_control.used_data import used_data


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


def data_specification(
    saved_json_path: Path,
    container_side_fastq_folder: Path = Path("/data/fastq"),
    container_side_meta_folder: Path = Path("/data/metadata"),
) -> Databank:
    """保存したjsonファイルからデータセットを読み込み、Databankを返す
    もしファイルが存在しない場合は、デフォルトのデータを返す。

    Args:
        saved_json_path (Path | None): 保存されたjsonファイルのパス
    """
    if saved_json_path is None or not saved_json_path.exists():
        return used_data(
            container_side_fastq_stored_path=container_side_fastq_folder,
            container_side_meta_stored_path=container_side_meta_folder,
        )
    else:
        json_data = saved_json_path.read_text()
        return Databank.from_json(json_data)


# def pipeline_run():
#     pipeline_ctn = provid_container()
#     with Executor(pipeline_ctn) as executor:
#         yield executor
#
