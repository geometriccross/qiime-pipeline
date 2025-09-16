#!/usr/bin/env python

from pathlib import Path
from scripts.pipeline import support
from .setup import PipelineContext


def command_list(
    context: PipelineContext, base_dir: Path, out_dir: Path
) -> list[support.Q2CmdAssembly]:
    # Import sequences
    import_cmd = (
        support.Q2CmdAssembly("qiime tools import")
        .add_option("type", "SampleData[PairedEndSequencesWithQuality]")
        .add_option("input-format", "PairedEndFastqManifestPhred33V2")
        .add_option("input-path", str(context.ctn_manifest))
        .add_option("output-path", out_dir / "paired_end_demux.qza")
    )

    # Get region settings from the first dataset
    dataset = next(iter(context.setting.datasets.sets))
    region = dataset.region

    dada2_cmd = (
        support.Q2CmdAssembly("qiime dada2 denoise-paired")
        .add_option("quiet")
        .add_input("demultiplexed-seqs", base_dir / "paired_end_demux.qza")
        .add_parameter("n-threads", "0")
        .add_parameter("trim-left-f", str(region.trim_left_f))
        .add_parameter("trim-left-r", str(region.trim_left_r))
        .add_parameter("trunc-len-f", str(region.trunc_len_f))
        .add_parameter("trunc-len-r", str(region.trunc_len_r))
        .add_output("table", out_dir / "denoised_table.qza")
        .add_output("representative-sequences", out_dir / "denoised_seq.qza")
        .add_output("denoising-stats", out_dir / "denoised_stats.qza")
    )

    phylogeny_cmd = (
        support.Q2CmdAssembly("qiime phylogeny align-to-tree-mafft-fasttree")
        .add_option("quiet")
        .add_input("sequences", base_dir / "denoised_seq.qza")
        .add_output("alignment", out_dir / "aligned-rep-seqs.qza")
        .add_output("masked-alignment", out_dir / "masked-aligned-rep-seqs.qza")
        .add_output("tree", out_dir / "unrooted-tree.qza")
        .add_output("rooted-tree", out_dir / "rooted-tree.qza")
    )

    # 実行時のエラーを避けるため
    # steps, iterationsはサンプルのmax featureよりも十分に小さくする
    rarefaction_cmd = (
        support.Q2CmdAssembly("qiime diversity alpha-rarefaction")
        .add_option("quiet")
        .add_parameter("min-depth", "1")
        .add_parameter("max-depth", context.setting.sampling_depth)
        .add_parameter(
            "steps", str(2) if context.setting.sampling_depth < 10 else str(10)
        )
        .add_parameter(
            "iterations", str(1) if context.setting.sampling_depth < 10 else str(10)
        )
        .add_metadata("metadata-file", str(context.ctn_metadata))
        .add_input("table", base_dir / "denoised_table.qza")
        .add_input("phylogeny", base_dir / "rooted-tree.qza")
        .add_output("visualization", out_dir / "alpha_rarefaction.qzv")
    )

    return [import_cmd, dada2_cmd, phylogeny_cmd, rarefaction_cmd]


def run_rarefaction(context: PipelineContext) -> Path:
    """
    Perform rarefaction analysis using QIIME2.

    Returns:
        Path to the generated QZV file
    """

    out_dir = context.setting.container_data.workspace_path
    base_dir = out_dir  # ここではout_dirとbase_dirは同じに設定
    context.executor.run(["bash", "-c", "apt update && apt upgrade -y"])
    context.executor.run(["mkdir", "-p", out_dir.as_posix()])

    for cmd in command_list(context, base_dir, out_dir):
        print(cmd)
        if isinstance(cmd, support.Q2CmdAssembly):
            cmd = cmd.build()

        context.executor.run(cmd)

    return out_dir / "alpha_rarefaction.qzv"


def copy_from_container(context: PipelineContext, ctn_target_file: Path) -> Path:
    out_dir = Path(f"out/{context.setting.batch_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy QZV file from container
    context.executor.run(
        ["docker", "cp", f"{context.setting.batch_id}:{ctn_target_file}", str(out_dir)]
    )

    return out_dir / ctn_target_file.name


def execute(context: PipelineContext) -> None:
    """
    Execute the full workflow of rarefaction analysis and sampling depth processing.
    """
    try:
        qzv_path = run_rarefaction(context)
        local_file = copy_from_container(context, qzv_path)
        support.QzvViewer().view(local_file)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        raise


if __name__ == "__main__":
    # This script is intended to be imported and used with SettingData,
    # not run directly from the command line
    pass
