import python_on_whales
from pathlib import Path
from src.pipeline.support import PipelineContext


def find(key: str, iterable: list) -> str:
    for file in iterable:
        if key in file:
            return file


def copy_from_container(context: PipelineContext, ctn_target_file: Path) -> Path:
    out_dir = context.setting.container_data.output_path.local_pos.joinpath(
        str(context.setting.batch_id)
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy QZV file from container
    python_on_whales.docker.copy(
        source=f"{context.setting.batch_id}:{ctn_target_file}", destination=str(out_dir)
    )

    return out_dir / ctn_target_file.name
