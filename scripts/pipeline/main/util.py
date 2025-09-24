from pathlib import Path
from .setup import PipelineContext


def find(key: str, iterable: list) -> str:
    for file in iterable:
        if key in file:
            return file


def copy_from_container(context: PipelineContext, ctn_target_file: Path) -> Path:
    out_dir = Path(f"out/{context.setting.batch_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy QZV file from container
    context.executor.run(
        ["docker", "cp", f"{context.setting.batch_id}:{ctn_target_file}", str(out_dir)]
    )

    return out_dir / ctn_target_file.name
