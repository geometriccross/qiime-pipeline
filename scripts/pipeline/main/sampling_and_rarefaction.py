#!/usr/bin/env python

from pathlib import Path
from scripts.data.store.setting_data_structure import SettingData
from scripts.pipeline.support.executor import Executor
from scripts.pipeline.support.qiime_command import QiimeCommandBuilder


def run_rarefaction(setting: SettingData, executor: Executor) -> Path:
    """
    Perform rarefaction analysis using QIIME2.

    Args:
        setting: Configuration settings
        executor: Docker container executor

    Returns:
        Path to the generated QZV file
    """
    # Create temporary directory for output
    tmp_dir = Path("/tmp/out")
    executor.run(["mkdir", "-p", str(tmp_dir)])

    # Import sequences
    import_cmd = (
        QiimeCommandBuilder("qiime tools import")
        .add_option("type", "'SampleData[PairedEndSequencesWithQuality]'")
        .add_option("input-format", "PairedEndFastqManifestPhred33V2")
        .add_option("input-path", str(setting.manifest_path))
        .add_option("output-path", "paired_end_demux.qza")
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
        .add_input("demultiplexed-seqs", "paired_end_demux.qza")
        .add_parameter("n-threads", "0")
        .add_parameter("trim-left-f", str(region.trim_left_f))
        .add_parameter("trim-left-r", str(region.trim_left_r))
        .add_parameter("trunc-len-f", str(region.trunc_len_f))
        .add_parameter("trunc-len-r", str(region.trunc_len_r))
        .add_output("table", "denoised_table.qza")
        .add_output("representative-sequences", "denoised_seq.qza")
        .add_output("denoising-stats", "denoised_stats.qza")
        .build()
    )
    executor.run(" ".join(dada2_cmd))

    # Perform phylogenetic analysis
    phylogeny_cmd = (
        QiimeCommandBuilder("qiime phylogeny align-to-tree-mafft-fasttree")
        .add_option("quiet")
        .add_input("sequences", "denoised_seq.qza")
        .add_output("alignment", "aligned-rep-seqs.qza")
        .add_output("masked-alignment", "masked-aligned-rep-seqs.qza")
        .add_output("tree", "unrooted-tree.qza")
        .add_output("rooted-tree", "rooted-tree.qza")
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
        .add_input("table", "denoised_table.qza")
        .add_input("phylogeny", "rooted-tree.qza")
        .add_output("visualization", "alpha_rarefaction.qzv")
        .build()
    )
    executor.run(" ".join(rarefaction_cmd))

    return Path("alpha_rarefaction.qzv")


def run_sampling_depth(
    setting: SettingData, executor: Executor, qzv_path: Path
) -> None:
    """
    Process the QZV file and run visualization.

    Args:
        setting: Configuration settings
        executor: Docker container executor
        qzv_path: Path to the QZV file to process
    """
    # Create output directory if it doesn't exist
    out_dir = Path(f"out/{setting.batch_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy QZV file from container
    executor.run(["docker", "cp", f"{setting.batch_id}:{qzv_path}", str(out_dir)])

    # Find QZV files and run view.sh
    for qzv_file in out_dir.glob("*.qzv"):
        executor.run(["./scripts/view.sh", str(qzv_file)])


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
        run_sampling_depth(setting, executor, qzv_path)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        raise


if __name__ == "__main__":
    # This script is intended to be imported and used with SettingData,
    # not run directly from the command line
    pass
