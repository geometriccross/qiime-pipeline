#!/usr/bin/env python

from pathlib import Path
from scripts.data.store import SettingData
from scripts.pipeline.support.executor import Executor
from scripts.pipeline.support.qiime_command import QiimeCommandBuilder
from scripts.pipeline.support.view import QzvViewer, ViewError


def run_rarefaction(setting: SettingData, executor: Executor) -> Path:
    """
    Perform rarefaction analysis using QIIME2.

    Args:
        setting: Configuration settings
        executor: Docker container executor

    Returns:
        Path to the generated QZV file
    """

    out_dir = Path(setting.workspace_path)
    base_dir = out_dir  # ここではout_dirとbase_dirは同じに設定
    executor.run(["mkdir", "-p", out_dir.as_posix()])

    # Import sequences
    import_cmd = (
        QiimeCommandBuilder("qiime tools import")
        .add_option("type", "'SampleData[PairedEndSequencesWithQuality]'")
        .add_option("input-format", "PairedEndFastqManifestPhred33V2")
        .add_option("input-path", str(setting.manifest_path))
        .add_option("output-path", out_dir / "paired_end_demux.qza")
        .build()
    )
    executor.run(" ".join(import_cmd))

    # Get region settings from the first dataset
    dataset = next(iter(setting.datasets.sets))
    region = dataset.region

    # Run DADA2 denoising with region-specific parameters
    dada2_cmd = (
        QiimeCommandBuilder("qiime dada2 denoise-paired")
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
        .build()
    )
    executor.run(" ".join(dada2_cmd))

    # Perform phylogenetic analysis
    phylogeny_cmd = (
        QiimeCommandBuilder("qiime phylogeny align-to-tree-mafft-fasttree")
        .add_option("quiet")
        .add_input("sequences", base_dir / "denoised_seq.qza")
        .add_output("alignment", out_dir / "aligned-rep-seqs.qza")
        .add_output("masked-alignment", out_dir / "masked-aligned-rep-seqs.qza")
        .add_output("tree", out_dir / "unrooted-tree.qza")
        .add_output("rooted-tree", out_dir / "rooted-tree.qza")
        .build()
    )
    executor.run(" ".join(phylogeny_cmd))

    # Generate alpha rarefaction
    rarefaction_cmd = (
        QiimeCommandBuilder("qiime diversity alpha-rarefaction")
        .add_option("quiet")
        .add_parameter("min-depth", "1")
        .add_parameter("max-depth", "50000")
        .add_metadata("metadata-file", str(setting.metadata_path))
        .add_input("table", base_dir / "denoised_table.qza")
        .add_input("phylogeny", base_dir / "rooted-tree.qza")
        .add_output("visualization", out_dir / "alpha_rarefaction.qzv")
        .build()
    )
    executor.run(" ".join(rarefaction_cmd))

    return out_dir / "alpha_rarefaction.qzv"


def copy_from_container(batch_id: str, executor: Executor, qzv_path: Path) -> None:
    """
    Process the QZV file and run visualization.

    Args:
        batch_id: Unique identifier for the batch
        executor: Docker container executor
        qzv_path: Path to the QZV file to process
    """
    # Create output directory if it doesn't exist
    out_dir = Path(f"out/{batch_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy QZV file from container
    executor.run(["docker", "cp", f"{batch_id}:{qzv_path}", str(out_dir)])


def view(qzv_path: Path) -> None:
    try:
        # Find QZV files and display using QzvViewer
        QzvViewer().view(qzv_path)
    except ViewError as e:
        print(f"Warning: Failed to display QZV file: {str(e)}")


def execute(setting: SettingData, executor: Executor) -> None:
    """
    Execute the full workflow of rarefaction analysis and sampling depth processing.

    Args:
        setting: Configuration settings
        executor: Docker container executor
    """
    try:
        # Run rarefaction and get QZV file path
        qzv_path = run_rarefaction(setting, executor)

        # Process the QZV file
        copy_from_container(setting.batch_id, executor, qzv_path)
        view(qzv_path)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        raise


if __name__ == "__main__":
    # This script is intended to be imported and used with SettingData,
    # not run directly from the command line
    pass
