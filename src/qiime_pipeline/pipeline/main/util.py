from pathlib import Path
import python_on_whales
from qiime_pipeline.pipeline.support import PipelineContext


def find(key: str, iterable: list) -> str:
    for file in iterable:
        if key in file:
            return file


def copy_from_container(context: PipelineContext, target: Path) -> Path:
    out_dir = context.setting.local_output_path.joinpath(
        str(context.setting.batch_id))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy QZV file from container
    python_on_whales.docker.copy(
        source=f"{context.setting.batch_id}:{target}", destination=str(out_dir)
    )

    return out_dir / target.name
