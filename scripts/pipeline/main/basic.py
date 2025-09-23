#!/usr/bin/env python

from pathlib import Path
from scripts.pipeline import support
from .setup import PipelineContext


def command_list(context: PipelineContext, out_dir: Path) -> support.Q2CmdAssembly:
    assembly = support.Q2CmdAssembly()
    # fmt: off

    pre_dir = out_dir / "pre"
    basic_dir = out_dir / "basic"
    core_dir = out_dir / "core"

    # Import sequences
    assembly.new_cmd("qiime tools import") \
        .add_option("type", "SampleData[PairedEndSequencesWithQuality]") \
        .add_option("input-format", "PairedEndFastqManifestPhred33V2") \
        .add_option("input-path", str(context.ctn_manifest)) \
        .add_option("output-path", pre_dir / "paired_end_demux.qza")

    dataset = next(iter(context.setting.datasets.sets))
    region = dataset.region

    # Denoise paired sequences
    assembly.new_cmd("qiime dada2 denoise-paired") \
        .add_option("quiet") \
        .add_input("demultiplexed-seqs", pre_dir / "paired_end_demux.qza") \
        .add_parameter("n-threads", "0") \
        .add_parameter("trim-left-f", str(region.trim_left_f)) \
        .add_parameter("trim-left-r", str(region.trim_left_r)) \
        .add_parameter("trunc-len-f", str(region.trunc_len_f)) \
        .add_parameter("trunc-len-r", str(region.trunc_len_r)) \
        .add_output("table", pre_dir / "denoised_table.qza") \
        .add_output("representative-sequences", pre_dir / "denoised_seq.qza") \
        .add_output("denoising-stats", pre_dir / "denoised_stats.qza")

    sampling_depth = context.setting.sampling_depth

    # Filter samples
    assembly.new_cmd("qiime feature-table filter-samples") \
        .add_option("quiet") \
        .add_input("table", pre_dir / "denoised_table.qza") \
        .add_parameter("min-frequency", str(sampling_depth)) \
        .add_output("filtered-table", pre_dir / "filtered_table.qza")

    # Filter sequences
    assembly.new_cmd("qiime feature-table filter-seqs") \
        .add_option("quiet") \
        .add_input("data", pre_dir / "denoised_seq.qza") \
        .add_input("table", pre_dir / "filtered_table.qza") \
        .add_output("filtered-data", pre_dir / "filtered_seq.qza")

    db_path = str(context.setting.container_data.database_path.local_pos)

    # Classify sequences
    assembly.new_cmd("qiime feature-classifier classify-sklearn") \
        .add_option("quiet") \
        .add_input("classifier", db_path) \
        .add_input("reads", pre_dir / "filtered_seq.qza") \
        .add_output("classification", pre_dir / "classification.qza")

    # Filter table by taxonomy
    assembly.new_cmd("qiime taxa filter-table") \
        .add_option("quiet") \
        .add_input("table", pre_dir / "filtered_table.qza") \
        .add_input("taxonomy", pre_dir / "classification.qza") \
        .add_parameter("exclude", "mitochondria,cyanobacteria") \
        .add_output("filtered-table", basic_dir / "common_biology_free_table.qza")

    # Filter sequences by taxonomy
    assembly.new_cmd("qiime taxa filter-seqs") \
        .add_option("quiet") \
        .add_parameter("exclude", "mitochondria,cyanobacteria") \
        .add_input("sequences", pre_dir / "filtered_seq.qza") \
        .add_input("taxonomy", pre_dir / "classification.qza") \
        .add_output(
            "filtered-sequences",
            basic_dir / "common_biology_free_seq.qza"
        )

    # Phylogenetic tree construction
    assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree") \
        .add_option("quiet") \
        .add_input("sequences", basic_dir / "common_biology_free_seq.qza") \
        .add_output(
            "alignment",
            basic_dir / "common_biology_free_aligned-rep-seqs.qza"
        ) \
        .add_output(
            "masked-alignment",
            basic_dir / "common_biology_free_masked-aligned-rep-seqs.qza"
        ) \
        .add_output("tree", basic_dir / "common_biology_free_unrooted-tree.qza") \
        .add_output("rooted-tree", basic_dir / "common_biology_free_rooted-tree.qza")

    # Classify filtered sequences
    assembly.new_cmd("qiime feature-classifier classify-sklearn") \
        .add_option("quiet") \
        .add_input("classifier", "/db/classifier.qza") \
        .add_input("reads", basic_dir / "common_biology_free_seq.qza") \
        .add_output(
            "classification",
            basic_dir / "common_biology_free_classification.qza"
        )

    # Core metrics calculation
    assembly.new_cmd("qiime diversity core-metrics-phylogenetic") \
        .add_option("quiet") \
        .add_input("phylogeny", basic_dir / "common_biology_free_rooted-tree.qza") \
        .add_input("table", basic_dir / "common_biology_free_table.qza") \
        .add_metadata("metadata-file", str(context.ctn_metadata)) \
        .add_parameter("sampling-depth", str(sampling_depth)) \
        .add_output("output-dir", core_dir)

    # fmt: on
    assembly.sort_commands()
    return assembly


def run_basic(context: PipelineContext) -> Path:
    """
    Run the basic QIIME2 analysis pipeline.

    Returns:
        Path to the output directory
    """
    pre_dir = Path(context.setting.container_data.output_path) / "pre"
    basic_dir = Path(context.setting.container_data.output_path) / "basic"
    core_dir = Path(context.setting.container_data.output_path) / "core"

    context.executor.run(["bash", "-c", "apt update && apt upgrade -y"])

    # Create necessary directories
    for dir_path in [pre_dir, basic_dir, core_dir]:
        context.executor.run(["mkdir", "-p", dir_path.as_posix()])

    [
        context.executor.run(cmd)
        for cmd in command_list(
            context, context.setting.container_data.output_path
        ).build_all()
    ]

    return core_dir


def execute(context: PipelineContext) -> None:
    """
    Execute the full basic analysis workflow.
    """
    try:
        run_basic(context)
        # Additional analysis scripts can be called here if needed
        # Note: In the original shell script, alpha.sh and beta.sh were sourced

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        raise
