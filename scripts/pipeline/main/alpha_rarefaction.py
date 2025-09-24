#!/usr/bin/env python

from pathlib import Path
from scripts.pipeline import support
from .setup import PipelineContext
from .util import copy_from_container


def command_list(
    context: PipelineContext, base_dir: Path, out_dir: Path
) -> support.Q2CmdAssembly:
    assembly = support.Q2CmdAssembly()
    # fmt: off

    # Import sequences
    imported = assembly.new_cmd("qiime tools import") \
        .add_option("type", "SampleData[PairedEndSequencesWithQuality]") \
        .add_option("input-format", "PairedEndFastqManifestPhred33V2") \
        .add_option("input-path", str(context.ctn_manifest)) \
        .add_option("output-path", out_dir / "paired_end_demux.qza") \
        .get_outputs()

    # Get region settings from the first dataset
    dataset = next(iter(context.setting.datasets.sets))
    region = dataset.region

    denoised_table, denoised_seq, denoised_stats =  \
        assembly.new_cmd("qiime dada2 denoise-paired") \
        .add_option("quiet") \
        .add_input("demultiplexed-seqs", imported) \
        .add_parameter("n-threads", "0") \
        .add_parameter("trim-left-f", str(region.trim_left_f)) \
        .add_parameter("trim-left-r", str(region.trim_left_r)) \
        .add_parameter("trunc-len-f", str(region.trunc_len_f)) \
        .add_parameter("trunc-len-r", str(region.trunc_len_r)) \
        .add_output("table", out_dir / "denoised_table.qza") \
        .add_output("representative-sequences", out_dir / "denoised_seq.qza") \
        .add_output("denoising-stats", out_dir / "denoised_stats.qza") \
        .get_outputs()

    align_seq, masked_align_seq, unrooted_tree, rooted_tree = \
        assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree") \
        .add_option("quiet") \
        .add_input("sequences", denoised_seq) \
        .add_output("alignment", out_dir / "aligned-rep-seqs.qza") \
        .add_output("masked-alignment", out_dir / "masked-aligned-rep-seqs.qza") \
        .add_output("tree", out_dir / "unrooted-tree.qza") \
        .add_output("rooted-tree", out_dir / "rooted-tree.qza") \
        .get_outputs()

    sampling_depth = context.setting.sampling_depth

    # 実行時のエラーを避けるため
    # steps, iterationsはサンプルのmax featureよりも十分に小さくする
    assembly.new_cmd("qiime diversity alpha-rarefaction") \
        .add_option("quiet") \
        .add_input("table", denoised_table) \
        .add_input("phylogeny", rooted_tree) \
        .add_parameter("min-depth", "1") \
        .add_parameter("max-depth", sampling_depth) \
        .add_parameter("steps", str(2) if sampling_depth < 10 else str(10)) \
        .add_parameter("iterations", str(1) if sampling_depth < 10 else str(10)) \
        .add_metadata("metadata-file", str(context.ctn_metadata)) \
        .add_output("visualization", out_dir / "alpha_rarefaction.qzv")

    # fmt: on

    assembly.sort_commands()
    return assembly


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

    [
        context.executor.run(cmd)
        for cmd in command_list(context, base_dir, out_dir).build_all()
    ]

    return out_dir / "alpha_rarefaction.qzv"


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
